# Ensures venv Python is used for tests regardless of terminal auto-activation.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$venvPy = Join-Path $root '.venv/Scripts/python.exe'
if (!(Test-Path $venvPy)) { throw "Venv python not found at $venvPy" }
& $venvPy -m pytest @args
