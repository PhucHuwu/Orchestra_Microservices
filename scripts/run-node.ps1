param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("host", "mixer", "guitar", "oboe", "aux")]
  [string]$Role,

  [Parameter(Mandatory = $true)]
  [string]$HostIp,

  [ValidateSet("cloud", "local")]
  [string]$DbMode = "cloud",

  [string]$MixerIp = "",
  [string]$GuitarIp = "",
  [string]$OboeIp = "",
  [string]$AuxIp = ""
)

$ErrorActionPreference = "Stop"

function Require-Command {
  param([Parameter(Mandatory = $true)][string]$Name)
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Required command not found: $Name"
  }
}

function Ensure-DockerReady {
  Require-Command -Name "docker"
  docker version *> $null
  if ($LASTEXITCODE -ne 0) {
    throw "Docker daemon is not available. Start Docker Desktop (Linux containers mode) and retry."
  }
}

function Get-PythonBootstrapCommand {
  if (Get-Command python -ErrorAction SilentlyContinue) {
    return @("python")
  }
  if (Get-Command py -ErrorAction SilentlyContinue) {
    return @("py", "-3")
  }
  return $null
}

function Ensure-BootstrapVenv {
  $pythonCmd = Get-PythonBootstrapCommand
  if ($null -eq $pythonCmd) {
    Write-Warning "Python is not installed on this machine. Skip topology bootstrap."
    Write-Warning "Install Python, then run: py -3 scripts/bootstrap_rabbitmq_topology.py"
    return $null
  }

  if (-not (Test-Path ".venv\Scripts\python.exe")) {
    if ($pythonCmd.Length -eq 1) {
      & $pythonCmd[0] -m venv .venv *> $null
    }
    else {
      & $pythonCmd[0] $pythonCmd[1] -m venv .venv *> $null
    }
  }

  $venvPython = ".venv\Scripts\python.exe"
  & $venvPython -m pip install --upgrade pip *> $null
  & $venvPython -m pip install pika *> $null
  return [string]$venvPython
}

function Invoke-BootstrapTopology {
  $venvPython = Ensure-BootstrapVenv
  if ($null -ne $venvPython) {
    & $venvPython scripts/bootstrap_rabbitmq_topology.py
    return
  }
}

Ensure-DockerReady

if ([string]::IsNullOrWhiteSpace($MixerIp)) { $MixerIp = $HostIp }
if ([string]::IsNullOrWhiteSpace($GuitarIp)) { $GuitarIp = $HostIp }
if ([string]::IsNullOrWhiteSpace($OboeIp)) { $OboeIp = $HostIp }
if ([string]::IsNullOrWhiteSpace($AuxIp)) { $AuxIp = $HostIp }

Copy-Item -Path ".env.example" -Destination ".env" -Force

function Set-EnvValue {
  param(
    [Parameter(Mandatory = $true)][string]$Key,
    [Parameter(Mandatory = $true)][string]$Value
  )

  $lines = Get-Content -Path ".env"
  $found = $false
  for ($i = 0; $i -lt $lines.Length; $i++) {
    if ($lines[$i] -match "^$Key=") {
      $lines[$i] = "$Key=$Value"
      $found = $true
      break
    }
  }
  if (-not $found) {
    $lines += "$Key=$Value"
  }
  Set-Content -Path ".env" -Value $lines
}

Set-EnvValue -Key "RABBITMQ_HOST" -Value $HostIp
Set-EnvValue -Key "RABBITMQ_URL" -Value "amqp://orchestra:orchestra@$HostIp`:5672/%2F"
Set-EnvValue -Key "RABBITMQ_MGMT_API_URL" -Value "http://$HostIp`:15672/api"

switch ($Role) {
  "host" {
    Set-EnvValue -Key "RABBITMQ_HOST" -Value "rabbitmq"
    Set-EnvValue -Key "RABBITMQ_URL" -Value "amqp://orchestra:orchestra@rabbitmq:5672/%2F"
    Set-EnvValue -Key "RABBITMQ_MGMT_API_URL" -Value "http://rabbitmq:15672/api"
    Set-EnvValue -Key "CONDUCTOR_BASE_URL" -Value "http://$HostIp`:8101"
    Set-EnvValue -Key "CONDUCTOR_SERVICE_URL" -Value "http://$HostIp`:8101"
    Set-EnvValue -Key "MIXER_SERVICE_URL" -Value "http://$MixerIp`:8301"
    Set-EnvValue -Key "GUITAR_SERVICE_URL" -Value "http://$GuitarIp`:8201"
    Set-EnvValue -Key "OBOE_SERVICE_URL" -Value "http://$OboeIp`:8202"
    Set-EnvValue -Key "DRUMS_SERVICE_URL" -Value "http://$AuxIp`:8203"
    Set-EnvValue -Key "BASS_SERVICE_URL" -Value "http://$AuxIp`:8203"
    Set-EnvValue -Key "NEXT_PUBLIC_API_BASE_URL" -Value "http://$HostIp`:8000"
    Set-EnvValue -Key "NEXT_PUBLIC_WS_URL" -Value "ws://$HostIp`:8000/ws/metrics"
    Set-EnvValue -Key "CORS_ALLOW_ORIGINS" -Value "http://$HostIp`:3000"

    if ($DbMode -eq "local") {
      docker compose --profile local-db up -d --build rabbitmq postgres conductor dashboard-api dashboard-web
    }
    else {
      docker compose up -d --build rabbitmq conductor dashboard-api dashboard-web
    }

    Invoke-BootstrapTopology
    docker compose logs -f rabbitmq conductor dashboard-api dashboard-web
  }
  "mixer" {
    docker compose up -d --build --no-deps mixer
    docker compose logs -f mixer
  }
  "guitar" {
    docker compose up -d --build --no-deps guitar-service
    docker compose logs -f guitar-service
  }
  "oboe" {
    docker compose up -d --build --no-deps oboe-service
    docker compose logs -f oboe-service
  }
  "aux" {
    docker compose up -d --build --no-deps drums-service
    docker compose logs -f drums-service
  }
}
