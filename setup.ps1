#Requires -Version 5.1
param(
    [switch]$Down,
    [switch]$Logs,
    [switch]$Rebuild
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Write-Step { param($msg) Write-Host "`n>>> $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "    [OK] $msg" -ForegroundColor Green }
function Write-Skip { param($msg) Write-Host "    [--] $msg" -ForegroundColor DarkGray }
function Write-Warn { param($msg) Write-Host "    [!!] $msg" -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "`n[ERRO] $msg" -ForegroundColor Red; exit 1 }

function New-HexSecret {
    param([int]$Bytes = 32)
    $rng = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
    $b   = New-Object 'System.Byte[]' $Bytes
    $rng.GetBytes($b)
    return ([System.BitConverter]::ToString($b)) -replace '-', ''
}

function Replace-EnvLine {
    param([string]$File, [string]$Key, [string]$Value)
    $lines    = Get-Content $File
    $replaced = $lines -replace "^${Key}=.*", "${Key}=${Value}"
    $replaced | Set-Content $File -Encoding UTF8
}

if (-not (Test-Path "docker-compose.yml")) {
    Write-Fail "Corre este script a partir da raiz do projecto (onde esta o docker-compose.yml)."
}

# --- Modo --Down
if ($Down) {
    Write-Step "A parar e remover containers..."
    & docker compose down
    Write-Ok "Containers removidos."
    exit 0
}

# --- Modo --Logs
if ($Logs) {
    & docker compose logs -f
    exit 0
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   CANTTOUCHME - Setup e Execucao          " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# 1. Pre-requisitos
# ---------------------------------------------------------------------------
Write-Step "1/5 - Verificar pre-requisitos"

try {
    & docker info | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "docker info falhou" }
    Write-Ok "Docker esta a correr."
} catch {
    Write-Fail "Docker nao esta disponivel ou nao esta a correr. Inicia o Docker Desktop e tenta novamente."
}

try {
    & docker compose version | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "docker compose nao disponivel" }
    Write-Ok "Docker Compose esta disponivel."
} catch {
    Write-Fail "Docker Compose nao encontrado. Actualiza o Docker Desktop."
}

# ---------------------------------------------------------------------------
# 2. Ficheiros .env
# ---------------------------------------------------------------------------
Write-Step "2/5 - Configurar ficheiros .env"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    $pgPass = New-HexSecret -Bytes 16
    Replace-EnvLine -File ".env" -Key "POSTGRES_PASSWORD" -Value $pgPass
    Write-Ok "Criado .env (POSTGRES_PASSWORD gerado)."
} else {
    Write-Skip ".env ja existe."
}

if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    $jwtSecret = New-HexSecret -Bytes 32
    $rsaSecret = New-HexSecret -Bytes 32
    Replace-EnvLine -File "backend\.env" -Key "JWT_SECRET_KEY"                   -Value $jwtSecret
    Replace-EnvLine -File "backend\.env" -Key "SYSTEM_RSA_KEY_ENCRYPTION_SECRET" -Value $rsaSecret
    Write-Ok "Criado backend/.env (JWT e RSA secrets gerados)."
} else {
    Write-Skip "backend/.env ja existe."
}

if (-not (Test-Path "frontend\.env")) {
    Copy-Item "frontend\.env.example" "frontend\.env"
    Write-Ok "Criado frontend/.env."
} else {
    Write-Skip "frontend/.env ja existe."
}

# ---------------------------------------------------------------------------
# 3. Build
# ---------------------------------------------------------------------------
Write-Step "3/5 - Build dos containers"

if ($Rebuild) {
    & docker compose build --no-cache
} else {
    & docker compose build
}
if ($LASTEXITCODE -ne 0) { Write-Fail "Falha no build. Verifica os logs acima." }
Write-Ok "Build concluido."

# ---------------------------------------------------------------------------
# 4. Arrancar servicos
# ---------------------------------------------------------------------------
Write-Step "4/5 - Arrancar servicos"

Write-Host "    Iniciando base de dados..." -ForegroundColor DarkGray
& docker compose up -d db
if ($LASTEXITCODE -ne 0) { Write-Fail "Nao foi possivel arrancar a base de dados." }

Write-Host "    A aguardar que a base de dados esteja pronta..." -ForegroundColor DarkGray
$maxWait = 60
$waited  = 0
while ($waited -lt $maxWait) {
    $status = & docker inspect --format "{{.State.Health.Status}}" canttouchme-db 2>$null
    if ($status -eq "healthy") { break }
    Start-Sleep -Seconds 2
    $waited += 2
}
if ($waited -ge $maxWait) { Write-Fail "Base de dados nao ficou pronta a tempo." }
Write-Ok "Base de dados pronta."

Write-Host "    Iniciando backend..." -ForegroundColor DarkGray
& docker compose up -d backend
if ($LASTEXITCODE -ne 0) { Write-Fail "Nao foi possivel arrancar o backend." }

Write-Host "    A aguardar que o backend esteja pronto..." -ForegroundColor DarkGray
$waited = 0
$ready  = $false
while ($waited -lt $maxWait) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { }
    Start-Sleep -Seconds 2
    $waited += 2
}
if ($ready) {
    Write-Ok "Backend pronto em http://localhost:8000"
} else {
    Write-Warn "Backend pode nao estar completamente pronto. Verifica: docker compose logs backend"
}

Write-Host "    Iniciando frontend..." -ForegroundColor DarkGray
& docker compose up -d frontend
if ($LASTEXITCODE -ne 0) { Write-Fail "Nao foi possivel arrancar o frontend." }
Write-Ok "Frontend a iniciar em http://localhost:5173"

# ---------------------------------------------------------------------------
# 5. Sumario
# ---------------------------------------------------------------------------
Write-Step "5/5 - Tudo pronto"

Write-Host ""
Write-Host "  Frontend : http://localhost:5173" -ForegroundColor White
Write-Host "  Backend  : http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs : http://localhost:8000/docs" -ForegroundColor White
Write-Host "  DB       : localhost:5432" -ForegroundColor White
Write-Host ""
Write-Host "  Comandos uteis:" -ForegroundColor DarkGray
Write-Host "    .\setup.ps1 -Logs     # seguir logs em tempo real" -ForegroundColor DarkGray
Write-Host "    .\setup.ps1 -Down     # parar e remover containers" -ForegroundColor DarkGray
Write-Host "    .\setup.ps1 -Rebuild  # reconstruir imagens do zero" -ForegroundColor DarkGray
Write-Host ""
