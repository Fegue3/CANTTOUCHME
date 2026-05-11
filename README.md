# CANTTOUCHME

Skeleton inicial do projeto CANTTOUCHME com:

- Backend FastAPI local
- Frontend React + TypeScript + Vite local
- PostgreSQL em Docker
- Endpoint de health para validar API e base de dados

Nesta fase ainda nao ha autenticacao, criptografia, registos ou migrations.

## Requisitos

- Python 3.13+
- Node.js 24+
- Docker Desktop

No Windows, usa `npm.cmd` em vez de `npm`, porque o PowerShell pode bloquear `npm.ps1`.

## Configuracao

Cria os ficheiros `.env` a partir dos exemplos:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
```

## Base de dados

```powershell
docker compose up -d db
```

PostgreSQL fica disponivel em:

```text
localhost:5432
database: canttouchme
user: canttouchme
password: canttouchme
```

Se aparecer um erro sobre `docker_engine`, abre o Docker Desktop e volta a correr o comando.

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints uteis:

- API: http://localhost:8000
- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs

## Frontend

Noutro terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Abrir:

```text
http://localhost:5173
```

A pagina inicial chama `GET /health` e mostra se a API e a base de dados estao online.

## Verificacao rapida

1. `docker compose up -d db`
2. Backend em `http://localhost:8000/health`
3. Frontend em `http://localhost:5173`
4. Confirmar na pagina que aparecem `API online` e `Database online`
