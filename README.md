# CANTTOUCHME

Livro de registos pessoal e seguro. Os registos sao cifrados, protegidos com HMAC e ligados em cadeia (blockchain local por utilizador). Nenhuma palavra-passe, chave derivada ou texto em claro e guardado na base de dados.

Stack: **Python + FastAPI** | **React + TypeScript + Vite** | **PostgreSQL** | **Docker**

---

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (inclui Docker Compose)

So e necessario ter o Docker instalado e a correr. Tudo o resto corre dentro de containers.

---

## Arranque rapido

### Windows (PowerShell)

```powershell
.\setup.ps1
```

### macOS / Linux

```bash
chmod +x setup.sh
./setup.sh
```

O script faz automaticamente:

1. Cria os ficheiros `.env` a partir dos `.env.example`
2. Gera segredos aleatorios para JWT e RSA
3. Faz build dos containers
4. Arranca a base de dados, o backend e o frontend por esta ordem
5. Aguarda que cada servico esteja pronto antes de avancar

Apos o arranque:

| Servico   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:5173        |
| Backend   | http://localhost:8000        |
| API Docs  | http://localhost:8000/docs   |

---

## Comandos uteis

```powershell
# Parar e remover containers
.\setup.ps1 -Down

# Seguir logs em tempo real
.\setup.ps1 -Logs

# Reconstruir imagens do zero
.\setup.ps1 -Rebuild

# Logs so do backend
docker compose logs -f backend
```

```bash
# Equivalente em bash
./setup.sh --down
./setup.sh --logs
./setup.sh --rebuild
```

---

## Paginas da aplicacao

| Rota            | Descricao                              |
|-----------------|----------------------------------------|
| `/register`     | Criar conta (escolha de cifra e HMAC)  |
| `/login`        | Autenticacao                           |
| `/app`          | Escrever novo registo                  |
| `/records`      | Ver registos anteriores com validacao  |
| `/chain-status` | Estado geral da blockchain do utilizador |

---

## Testes

Com os containers a correr, abrir um terminal na pasta `backend` e correr:

```powershell
# Windows
docker compose exec backend python -m pytest -v
```

```bash
# macOS / Linux
docker compose exec backend python -m pytest -v
```

---

## Decisoes de seguranca

| Componente              | Escolha                                      |
|-------------------------|----------------------------------------------|
| Hash da palavra-passe   | bcrypt cost 12                               |
| Derivacao de chaves     | PBKDF2-HMAC-SHA256, 600 000 iteracoes        |
| Chave de cifra          | 128 bits, salt proprio                       |
| Chave de integridade    | 256 bits, salt proprio e diferente           |
| Cifras disponiveis      | AES-128-CBC ou AES-128-CTR (escolha no registo) |
| HMAC disponivel         | HMAC-SHA256 ou HMAC-SHA512 (escolha no registo) |
| Hash do bloco           | SHA-256                                      |
| Assinatura digital      | RSA-PSS com SHA-256, chave de 2048 bits      |
| Expiracao JWT / sessao  | 30 minutos                                   |
| Chave privada RSA       | Cifrada na base de dados com `SYSTEM_RSA_KEY_ENCRYPTION_SECRET` |

---

## Demonstracao do ataque

O ataque demonstra que um adversario com acesso directo a base de dados nao consegue alterar registos sem ser detectado.

**1. Preparar dados**
- Registar um utilizador
- Criar pelo menos tres registos
- Confirmar em `/records` que todos os blocos estao validos

**2. Aceder directamente ao PostgreSQL**

```powershell
docker exec -it canttouchme-db psql -U canttouchme -d canttouchme
```

**3. Alterar um bloco antigo** (escolher uma opcao)

```sql
-- Opcao A: corromper o ciphertext
UPDATE records SET ciphertext = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==' WHERE block_index = 1;

-- Opcao B: apagar um bloco intermedio
DELETE FROM records WHERE block_index = 2;

-- Opcao C: falsificar o previous_hash
UPDATE records SET previous_hash = 'FALSIFICADO' WHERE block_index = 2;
```

```sql
\q
```

**4. Resultado esperado**
- O bloco alterado aparece como invalido em `/records`
- Os blocos seguintes aparecem como `chain_affected`
- `/chain-status` mostra a cadeia como invalida

Ver [docs/attack_demo.md](docs/attack_demo.md) para mais detalhes.

---

## Estrutura do projecto

```
canttouchme/
  backend/          Python + FastAPI
  frontend/         React + TypeScript + Vite
  docs/             Especificacao e demo do ataque
  docker-compose.yml
  setup.ps1         Script de arranque (Windows)
  setup.sh          Script de arranque (macOS/Linux)
```
