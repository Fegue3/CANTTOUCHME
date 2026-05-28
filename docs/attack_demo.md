# Demonstração do Ataque — Brute-Force com Rate Limiting

## Tipo de ataque

**Brute-Force Login** — tentativa exaustiva de passwords num endpoint de autenticação.

O atacante conhece ou suspeita do email da vítima e envia pedidos repetidos ao
`POST /auth/login` com passwords diferentes, na esperança de acertar. Sem qualquer
proteção, a API responde a todos os pedidos sem limite.

---

## Contexto: por que este endpoint é um alvo

O FastAPI expõe documentação pública em `/docs` sem autenticação. Qualquer atacante
que descubra o endereço do backend vê imediatamente:

- o endpoint `POST /auth/login` com o schema `{ email, password }`;
- que um login bem-sucedido devolve um JWT que dá acesso a todos os registos da vítima decifrados.

Comprometer o login é, portanto, o caminho direto para comprometer todos os dados.

---

## Fluxo do ataque (sem defesa)

```
Atacante                          Servidor
   |                                  |
   |-- POST /auth/login {pw: "abc"} ->|
   |<----- 401 Unauthorized ----------|
   |                                  |
   |-- POST /auth/login {pw: "123"} ->|
   |<----- 401 Unauthorized ----------|
   |                                  |
   |         ... N tentativas ...     |
   |                                  |
   |-- POST /auth/login {pw: "ok"} -->|
   |<----- 200 OK  +  JWT token ------|
   |                                  |
   |--> GET /records (Bearer JWT) --->|
   |<----- registos em texto claro ---|
```

Sem rate limiting, o atacante pode testar milhares de passwords por minuto.

---

## Defesa: Rate Limiting

A aplicação usa `slowapi` para limitar pedidos por endereço IP:

| Endpoint                    | Limite      | Justificação                        |
|-----------------------------|-------------|-------------------------------------|
| `POST /auth/login`          | 5 / minuto  | Bloqueia brute-force no login       |
| `POST /auth/register`       | 3 / minuto  | Previne criação massiva de contas   |
| `GET /records`              | 30 / minuto | Limita exfiltração com token roubado|
| `POST /records`             | 20 / minuto | Previne spam de registos            |
| `GET /records/chain/status` | 20 / minuto | Protege operação computacionalmente pesada |
| `GET /records/{id}/verify`  | 30 / minuto | Idem                                |

Ao exceder o limite, o servidor responde com **429 Too Many Requests** e um header
`Retry-After` a indicar quantos segundos esperar.

---

## Fluxo do ataque (com defesa)

```
Atacante                          Servidor (Rate Limiter ativo)
   |                                  |
   |-- POST /auth/login {pw: "abc"} ->|  ← pedido 1  → 401
   |-- POST /auth/login {pw: "123"} ->|  ← pedido 2  → 401
   |-- POST /auth/login {pw: "qwe"} ->|  ← pedido 3  → 401
   |-- POST /auth/login {pw: "pw1"} ->|  ← pedido 4  → 401
   |-- POST /auth/login {pw: "pw2"} ->|  ← pedido 5  → 401
   |                                  |
   |-- POST /auth/login {pw: "pw3"} ->|  ← pedido 6  → 429 BLOQUEADO
   |-- POST /auth/login {pw: "pw4"} ->|  ← pedido 7  → 429 BLOQUEADO
   |-- POST /auth/login {pw: "pw5"} ->|  ← pedido 8  → 429 BLOQUEADO
   |         ...                      |
   |<-- Retry-After: 54s -------------|
```

O atacante fica bloqueado ao 6.º pedido e só pode tentar novamente após ~1 minuto,
tornando o brute-force inviável.

---

## Executar a demonstração

### 1. Arrancar a aplicação

```powershell
.\setup.ps1
```

### 2. Registar uma conta-alvo (uma vez)

Criar um utilizador através do frontend em `http://localhost:5173/register`, ou via API:

```powershell
curl -X POST http://localhost:8000/auth/register `
  -H "Content-Type: application/json" `
  -d '{"email":"<email-alvo>","password":"<password>","encryption_algorithm":"AES_CBC","hmac_algorithm":"HMAC_SHA256"}'
```

### 3. Correr o script de ataque

```bash
python attack_brute_force_demo.py --target <email-alvo>
```

O script tenta 20 passwords da wordlist sequencialmente e mostra o resultado de
cada tentativa em tempo real.

---

## Resultado esperado

```
[*] Alvo:    <email-alvo>
[*] Endpoint: http://localhost:8000/auth/login
[*] Wordlist: 20 passwords

    Tentativa 01  |  password: 'password'      →  401 Unauthorized  (42ms)
    Tentativa 02  |  password: '123456'         →  401 Unauthorized  (41ms)
    Tentativa 03  |  password: 'qwerty'         →  401 Unauthorized  (40ms)
    Tentativa 04  |  password: 'letmein'        →  401 Unauthorized  (39ms)
    Tentativa 05  |  password: 'admin'          →  401 Unauthorized  (38ms)
[!] Tentativa 06  |  password: 'welcome'        →  429 Too Many Requests  (12ms)  —  BLOQUEADO! (retry após 54s)
[!] Tentativa 07  |  password: 'monkey'         →  429 Too Many Requests  (11ms)  —  BLOQUEADO! (retry após 53s)
...

══════════════════ SUMÁRIO ══════════════════
  Total de tentativas : 20
  Logins bem-sucedidos : 0
  Pedidos bloqueados   : 15
  Erros / sem resposta : 0

[✓] Rate limiting funcionou! 15 pedido(s) bloqueados com 429.
```

---

## O que o diagrama de ataque deve mostrar

1. **Atacante** envia rajada de pedidos `POST /auth/login`
2. **Rate Limiter** (componente entre atacante e API) conta pedidos por IP
3. Pedidos 1–5 passam → API responde `401`
4. Pedidos 6+ são rejeitados pelo Rate Limiter → `429` sem chegar à lógica de negócio
5. **Base de dados** não é sequer consultada após o bloqueio

Componentes relevantes no diagrama: Atacante → [Rate Limiter / slowapi] → FastAPI → PostgreSQL
