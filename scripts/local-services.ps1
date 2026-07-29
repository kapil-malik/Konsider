[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("start", "stop", "restart")]
    [string]$Action
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$RunDirectory = Join-Path $RepoRoot ".konsider-run"
$StatePath = Join-Path $RunDirectory "services.json"
$WebRoot = Join-Path $RepoRoot "web"

function Resolve-Runtime {
    param(
        [string]$Override,
        [string[]]$Candidates,
        [string[]]$FallbackCandidates,
        [string[]]$CommandNames,
        [string]$Label
    )

    if ($Override) {
        if (-not (Test-Path -LiteralPath $Override -PathType Leaf)) {
            throw "$Label override does not exist: $Override"
        }
        return (Resolve-Path -LiteralPath $Override).Path
    }

    foreach ($candidate in $Candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    foreach ($commandName in $CommandNames) {
        $command = Get-Command $commandName -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Source
        }
    }

    foreach ($candidate in $FallbackCandidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    throw "$Label was not found. Complete the local setup or set its KONSIDER_* override."
}

function Assert-PortAvailable {
    param(
        [int]$Port,
        [string]$Label
    )

    $listener = [System.Net.Sockets.TcpListener]::new(
        [System.Net.IPAddress]::Loopback,
        $Port
    )
    try {
        $listener.Start()
    }
    catch {
        throw "$Label cannot start because port $Port is already in use."
    }
    finally {
        $listener.Stop()
    }
}

function Test-PythonReady {
    param([string]$Path)

    $previousErrorAction = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $null = & $Path -c "import uvicorn; import konsider" 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
    }
    return $exitCode -eq 0
}

function Get-ManagedProcesses {
    if (-not (Test-Path -LiteralPath $StatePath -PathType Leaf)) {
        return @()
    }

    try {
        $state = Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json
    }
    catch {
        throw "Cannot read $StatePath. Remove it only after confirming Konsider is stopped."
    }

    $managed = @()
    foreach ($serviceName in @("api", "ui")) {
        $entry = $state.$serviceName
        if (-not $entry) {
            continue
        }

        $process = Get-Process -Id ([int]$entry.pid) -ErrorAction SilentlyContinue
        if (-not $process) {
            continue
        }

        try {
            $actualStart = $process.StartTime.ToUniversalTime().Ticks
        }
        catch {
            continue
        }

        if ($actualStart -eq [long]$entry.start_time_utc_ticks) {
            $managed += [pscustomobject]@{
                Service = $serviceName
                Process = $process
            }
        }
    }
    return $managed
}

function Wait-ForUrl {
    param(
        [string]$Url,
        [string]$Label
    )

    $deadline = (Get-Date).AddSeconds(30)
    do {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
            if ($response.StatusCode -eq 200) {
                return
            }
        }
        catch {
            Start-Sleep -Milliseconds 500
        }
    } while ((Get-Date) -lt $deadline)

    throw "$Label did not become ready within 30 seconds. See $RunDirectory for logs."
}

function Start-Services {
    $running = @(Get-ManagedProcesses)
    if ($running.Count -gt 0) {
        $summary = ($running | ForEach-Object { "$($_.Service) PID $($_.Process.Id)" }) -join ", "
        throw "Konsider is already running ($summary). Use restart-local.cmd to restart it."
    }

    if (Test-Path -LiteralPath $StatePath) {
        Remove-Item -LiteralPath $StatePath -Force
    }
    New-Item -ItemType Directory -Path $RunDirectory -Force | Out-Null
    Assert-PortAvailable -Port 8000 -Label "API"
    Assert-PortAvailable -Port 5173 -Label "UI"

    $codexDependencies = Join-Path $HOME ".cache\codex-runtimes\codex-primary-runtime\dependencies"
    $python = Resolve-Runtime `
        -Override $env:KONSIDER_PYTHON `
        -Candidates @(
            (Join-Path $RepoRoot ".venv\Scripts\python.exe")
        ) `
        -FallbackCandidates @((Join-Path $codexDependencies "python\python.exe")) `
        -CommandNames @("python.exe", "python") `
        -Label "Python"
    $codexPython = Join-Path $codexDependencies "python\python.exe"
    if (-not (Test-PythonReady -Path $python)) {
        if (-not $env:KONSIDER_PYTHON -and
            (Test-Path -LiteralPath $codexPython -PathType Leaf) -and
            (Test-PythonReady -Path $codexPython)) {
            $python = $codexPython
        }
        else {
            throw "Python at '$python' does not have Konsider and Uvicorn installed. Complete the local setup or set KONSIDER_PYTHON."
        }
    }
    $node = Resolve-Runtime `
        -Override $env:KONSIDER_NODE `
        -Candidates @() `
        -FallbackCandidates @((Join-Path $codexDependencies "node\bin\node.exe")) `
        -CommandNames @("node.exe", "node") `
        -Label "Node.js"

    $viteScript = Join-Path $WebRoot "node_modules\vite\bin\vite.js"
    if (-not (Test-Path -LiteralPath $viteScript -PathType Leaf)) {
        throw "Frontend dependencies are missing. Run 'pnpm install' in $WebRoot first."
    }

    $api = $null
    $ui = $null
    try {
        $previousCors = [Environment]::GetEnvironmentVariable("KONSIDER_CORS_ORIGINS", "Process")
        [Environment]::SetEnvironmentVariable(
            "KONSIDER_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
            "Process"
        )
        try {
            $api = Start-Process `
                -FilePath $python `
                -ArgumentList @(
                    "-m", "uvicorn", "konsider.api.app:app",
                    "--host", "127.0.0.1", "--port", "8000", "--log-level", "info"
                ) `
                -WorkingDirectory $RepoRoot `
                -WindowStyle Hidden `
                -RedirectStandardOutput (Join-Path $RunDirectory "api.out.log") `
                -RedirectStandardError (Join-Path $RunDirectory "api.err.log") `
                -PassThru
        }
        finally {
            [Environment]::SetEnvironmentVariable(
                "KONSIDER_CORS_ORIGINS",
                $previousCors,
                "Process"
            )
        }

        $ui = Start-Process `
            -FilePath $node `
            -ArgumentList @($viteScript, "--host", "127.0.0.1", "--port", "5173") `
            -WorkingDirectory $WebRoot `
            -WindowStyle Hidden `
            -RedirectStandardOutput (Join-Path $RunDirectory "ui.out.log") `
            -RedirectStandardError (Join-Path $RunDirectory "ui.err.log") `
            -PassThru

        $api.Refresh()
        $ui.Refresh()
        @{
            api = @{
                pid = $api.Id
                start_time_utc_ticks = $api.StartTime.ToUniversalTime().Ticks
            }
            ui = @{
                pid = $ui.Id
                start_time_utc_ticks = $ui.StartTime.ToUniversalTime().Ticks
            }
        } | ConvertTo-Json | Set-Content -LiteralPath $StatePath -Encoding UTF8

        Wait-ForUrl -Url "http://127.0.0.1:8000/api/v2/health" -Label "API"
        Wait-ForUrl -Url "http://127.0.0.1:5173" -Label "UI"

        Write-Host "Konsider started."
        Write-Host "  UI:       http://127.0.0.1:5173"
        Write-Host "  API docs: http://127.0.0.1:8000/docs"
        Write-Host "  PIDs:     API $($api.Id), UI $($ui.Id)"
    }
    catch {
        foreach ($process in @($ui, $api)) {
            if ($process -and -not $process.HasExited) {
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            }
        }
        Remove-Item -LiteralPath $StatePath -Force -ErrorAction SilentlyContinue
        throw
    }
}

function Stop-Services {
    $running = @(Get-ManagedProcesses)
    if ($running.Count -eq 0) {
        Remove-Item -LiteralPath $StatePath -Force -ErrorAction SilentlyContinue
        Write-Host "Konsider is already stopped."
        return
    }

    foreach ($serviceName in @("ui", "api")) {
        $entry = $running | Where-Object { $_.Service -eq $serviceName }
        if ($entry) {
            Stop-Process -Id $entry.Process.Id -Force
            Wait-Process -Id $entry.Process.Id -Timeout 10 -ErrorAction SilentlyContinue
            Write-Host "Stopped $serviceName (PID $($entry.Process.Id))."
        }
    }
    Remove-Item -LiteralPath $StatePath -Force -ErrorAction SilentlyContinue
}

switch ($Action) {
    "start" { Start-Services }
    "stop" { Stop-Services }
    "restart" {
        Stop-Services
        Start-Services
    }
}
