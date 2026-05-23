#!/usr/bin/env bash
# CANTTOUCHME — setup e execucao completa do projecto.
#
# Uso:
#   ./setup.sh              # setup + arranque completo
#   ./setup.sh --down       # para e remove os containers
#   ./setup.sh --logs       # segue os logs de todos os servicos
#   ./setup.sh --rebuild    # forca rebuild das imagens (--no-cache)

set -euo pipefail

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
RED='\033[0;31m'; GRAY='\033[0;90m'; RESET='\033[0m'

step() { echo -e "\n${CYAN}>>> $1${RESET}"; }
ok()   { echo -e "    ${GREEN}[OK]${RESET} $1"; }
skip() { echo -e "    ${GRAY}[--]${RESET} $1"; }
warn() { echo -e "    ${YELLOW}[!!]${RESET} $1"; }
fail() { echo -e "\n${RED}[ERRO]${RESET} $1" >&2; exit 1; }

new_hex_secret() {
    # $1 = numero de bytes (default 32)
    local bytes="${1:-32}"
    if command -v openssl &>/dev/null; then
        openssl rand -hex "$bytes"
    else
        # fallback: /dev/urandom
        cat /dev/urandom | tr -dc 'a-f0-9' | head -c $((bytes * 2))
    fi
}

replace_env_line() {
    # $1=ficheiro  $2=chave  $3=valor
    local file="$1" key="$2" value="$3"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^${key}=.*|${key}=${value}|" "$file"
    else
        sed -i "s|^${key}=.*|${key}=${value}|" "$file"
    fi
}

# ---------------------------------------------------------------------------
# Verificar directorio
# ---------------------------------------------------------------------------
if [[ ! -f "docker-compose.yml" ]]; then
    fail "Corre este script a partir da raiz do projecto (onde esta o docker-compose.yml)."
fi

# ---------------------------------------------------------------------------
# Argumentos
# ---------------------------------------------------------------------------
MODE="start"
REBUILD_FLAG=""

for arg in "$@"; do
    case "$arg" in
        --down)    MODE="down" ;;
        --logs)    MODE="logs" ;;
        --rebuild) REBUILD_FLAG="--no-cache" ;;
    esac
done

# ---------------------------------------------------------------------------
# Modo --down
# ---------------------------------------------------------------------------
if [[ "$MODE" == "down" ]]; then
    step "A parar e remover containers..."
    docker compose down
    ok "Containers removidos."
    exit 0
fi

# ---------------------------------------------------------------------------
# Modo --logs
# ---------------------------------------------------------------------------
if [[ "$MODE" == "logs" ]]; then
    docker compose logs -f
    exit 0
fi

echo ""
echo -e "${CYAN}============================================${RESET}"
echo -e "${CYAN}   CANTTOUCHME  —  Setup e Execucao        ${RESET}"
echo -e "${CYAN}============================================${RESET}"

# ---------------------------------------------------------------------------
# 1. Verificar pre-requisitos
# ---------------------------------------------------------------------------
step "1/5 — Verificar pre-requisitos"

if ! command -v docker &>/dev/null; then
    fail "Docker nao esta instalado. Instala Docker Desktop e tenta novamente."
fi

if ! docker info &>/dev/null; then
    fail "Docker nao esta a correr. Inicia o Docker Desktop e tenta novamente."
fi
ok "Docker esta a correr."

if docker compose version &>/dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
else
    fail "Docker Compose nao encontrado. Actualiza o Docker Desktop para uma versao recente."
fi
ok "Docker Compose disponivel ($($COMPOSE_CMD version --short 2>/dev/null || echo 'ok'))."

# ---------------------------------------------------------------------------
# 2. Configurar ficheiros .env
# ---------------------------------------------------------------------------
step "2/5 — Configurar ficheiros .env"

# Root .env (credenciais da base de dados)
if [[ ! -f ".env" ]]; then
    cp .env.example .env
    pg_pass=$(new_hex_secret 16)
    replace_env_line ".env" "POSTGRES_PASSWORD" "$pg_pass"
    ok "Criado .env (POSTGRES_PASSWORD gerado)."
else
    skip ".env ja existe."
fi

# Backend .env
if [[ ! -f "backend/.env" ]]; then
    cp backend/.env.example backend/.env
    jwt_secret=$(new_hex_secret 32)
    rsa_secret=$(new_hex_secret 32)
    replace_env_line "backend/.env" "JWT_SECRET_KEY"                   "$jwt_secret"
    replace_env_line "backend/.env" "SYSTEM_RSA_KEY_ENCRYPTION_SECRET" "$rsa_secret"
    ok "Criado backend/.env (JWT_SECRET_KEY e SYSTEM_RSA_KEY_ENCRYPTION_SECRET gerados)."
else
    skip "backend/.env ja existe."
fi

# Frontend .env
if [[ ! -f "frontend/.env" ]]; then
    cp frontend/.env.example frontend/.env
    ok "Criado frontend/.env."
else
    skip "frontend/.env ja existe."
fi

# ---------------------------------------------------------------------------
# 3. Build dos containers
# ---------------------------------------------------------------------------
step "3/5 — Build dos containers"

# shellcheck disable=SC2086
$COMPOSE_CMD build $REBUILD_FLAG
ok "Build concluido."

# ---------------------------------------------------------------------------
# 4. Arrancar servicos: DB → Backend → Frontend
# ---------------------------------------------------------------------------
step "4/5 — Arrancar servicos"

# Base de dados
echo -e "    ${GRAY}Iniciando base de dados...${RESET}"
$COMPOSE_CMD up -d db

echo -e "    ${GRAY}A aguardar que a base de dados esteja pronta...${RESET}"
max_wait=60
waited=0
while [[ $waited -lt $max_wait ]]; do
    status=$(docker inspect --format='{{.State.Health.Status}}' canttouchme-db 2>/dev/null || echo "")
    [[ "$status" == "healthy" ]] && break
    sleep 2
    waited=$((waited + 2))
done
[[ $waited -ge $max_wait ]] && fail "Base de dados nao ficou pronta a tempo. Verifica: docker compose logs db"
ok "Base de dados pronta."

# Backend
echo -e "    ${GRAY}Iniciando backend...${RESET}"
$COMPOSE_CMD up -d backend

echo -e "    ${GRAY}A aguardar que o backend esteja pronto...${RESET}"
waited=0
while [[ $waited -lt $max_wait ]]; do
    if curl -sf "http://localhost:8000/health" &>/dev/null; then
        break
    fi
    sleep 2
    waited=$((waited + 2))
done
if [[ $waited -ge $max_wait ]]; then
    warn "Backend pode nao estar completamente pronto. Verifica com: docker compose logs backend"
else
    ok "Backend pronto em http://localhost:8000"
fi

# Frontend
echo -e "    ${GRAY}Iniciando frontend...${RESET}"
$COMPOSE_CMD up -d frontend
ok "Frontend a iniciar em http://localhost:5173"

# ---------------------------------------------------------------------------
# 5. Sumario
# ---------------------------------------------------------------------------
step "5/5 — Tudo pronto"

echo ""
echo -e "  Frontend  : ${GREEN}http://localhost:5173${RESET}"
echo -e "  Backend   : ${GREEN}http://localhost:8000${RESET}"
echo -e "  API Docs  : ${GREEN}http://localhost:8000/docs${RESET}"
echo -e "  DB        : ${GRAY}localhost:5432  (PostgreSQL)${RESET}"
echo ""
echo -e "  ${GRAY}Comandos uteis:${RESET}"
echo -e "  ${GRAY}  ./setup.sh --logs     # seguir logs em tempo real${RESET}"
echo -e "  ${GRAY}  ./setup.sh --down     # parar e remover containers${RESET}"
echo -e "  ${GRAY}  ./setup.sh --rebuild  # reconstruir imagens do zero${RESET}"
echo -e "  ${GRAY}  docker compose logs -f backend   # logs so do backend${RESET}"
echo ""
