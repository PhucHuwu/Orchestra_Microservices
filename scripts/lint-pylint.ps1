Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "[pylint] conductor"
Push-Location "conductor"
python -m pylint app tests
Pop-Location

Write-Host "[pylint] mixer"
Push-Location "mixer"
python -m pylint app tests
Pop-Location

Write-Host "[pylint] dashboard/backend"
Push-Location "dashboard/backend"
python -m pylint app tests
Pop-Location

Write-Host "[pylint] services"
python -m pylint services

Write-Host "[pylint] scripts"
python -m pylint scripts
