# Local setup

Konsider requires Python 3.11 or newer. Run worker commands from the repository root because worker
storage defaults are relative paths. API defaults are resolved from the installed source location
and do not depend on the current working directory.

## PowerShell

```powershell
git clone https://github.com/kapil-malik/Konsider.git
Set-Location Konsider
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Bash

```bash
git clone https://github.com/kapil-malik/Konsider.git
cd Konsider
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

No external service is needed to read the committed active release or run the API. A refresh needs
outbound HTTPS access to the registered official sources. Full release replay additionally needs the
ignored raw bytes previously captured under `data/raw/`; a clean checkout skips those replay tests.

## Verify the checkout

```bash
pytest
ruff check .
black --check .
python -m compileall -q src tests
```

GitHub Actions runs these four gates on Ubuntu for pushes and pull requests. See the
[worker guide](worker.md), [API guide](api.md), and [local deployment guide](deployment-local.md).
