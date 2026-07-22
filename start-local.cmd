@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\local-services.ps1" start
exit /b %ERRORLEVEL%
