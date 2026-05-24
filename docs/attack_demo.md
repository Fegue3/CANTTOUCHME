# Demonstração do Ataque

## Objetivo

Mostrar que um adversário que consiga obter o token de sessão de um utilizador
consegue ler todos os registos em texto claro — apesar de estarem cifrados na base
de dados — sem precisar de acesso direto ao PostgreSQL, sem conhecer a palavra-passe
e sem quebrar qualquer primitiva criptográfica.

---

## Como funciona a sessão na aplicação

Quando um utilizador faz login, o backend:

1. Valida a palavra-passe com bcrypt.
2. Deriva as chaves de cifra e integridade a partir da palavra-passe.
3. Guarda essas chaves em memória associadas a um `session_id` aleatório.
4. Emite um **JWT** que contém o `user_id` e o `session_id`.

O frontend guarda esse JWT em `sessionStorage` com a chave `canttouchme_token`.

Em cada pedido subsequente, o frontend envia o JWT no cabeçalho
`Authorization: Bearer <token>`. O backend valida o JWT, recupera as chaves da sessão
em memória, e usa-as para decifrar os registos antes de os devolver.

**Consequência:** quem tiver o JWT consegue pedir os registos ao backend e recebê-los
em texto limpo. O backend faz toda a decifra. O atacante não precisa de saber a
palavra-passe nem de ter acesso à base de dados.

---

## Superfície de ataque: sessionStorage

`sessionStorage` é um espaço de armazenamento do browser acessível a qualquer
JavaScript que corra na mesma origem (mesmo protocolo, domínio e porta).

Isto significa que:

- Um script malicioso injetado via XSS na aplicação pode ler o token.
- Alguém com acesso físico ao browser pode ler o token pela consola de
  desenvolvimento.
- Uma extensão de browser com permissões sobre a página pode ler o token.

`sessionStorage` é ligeiramente melhor do que `localStorage` porque o token
desaparece quando o separador ou o browser é fechado, mas continua a ser acessível
a qualquer JavaScript durante a sessão ativa.

---

## Preparação

Arrancar a aplicação:

```powershell
.\setup.ps1
```

Na aplicação (http://localhost:5173):

1. Criar uma conta em `/register`.
2. Iniciar sessão em `/login`.
3. Escrever **pelo menos três registos** em `/app` — usar conteúdo realista, por
   exemplo datas, nomes de pessoas ou informação pessoal.
4. Abrir `/records` e confirmar que todos os registos aparecem decifrados e válidos.

---

## Executar o ataque

### Passo 1 — Roubar o token de sessão

Abrir as ferramentas de desenvolvimento do browser (`F12`) e ir à consola.
Executar:

```javascript
const token = sessionStorage.getItem('canttouchme_token');
console.log(token);
```

O JWT aparece na consola. Copiar o valor — é uma string longa que começa por
`eyJ`.

Este passo simula o que um script XSS faria automaticamente e silenciosamente:
ler o token e enviá-lo para um servidor controlado pelo atacante.

### Passo 2 — Exfiltrar todos os registos em texto claro

Na máquina do atacante, com o token copiado, executar:

```python
import requests

TOKEN = "eyJ..."  # colar aqui o token copiado no passo 1

resposta = requests.get(
    "http://localhost:8000/records?page_size=50",
    headers={"Authorization": f"Bearer {TOKEN}"},
)

dados = resposta.json()
print(f"Total de registos: {dados['total']}\n")

for registo in dados["records"]:
    print(f"--- Bloco {registo['block_index']} ({registo['timestamp']}) ---")
    print(registo["text"])
    print()
```

---

## Resultado esperado

O script imprime todos os registos em texto limpo, ordenados por bloco.

Exemplo de saída:

```
Total de registos: 3

--- Bloco 1 (2026-05-20T10:15:00Z) ---
Hoje tive uma reunião difícil com o meu chefe. Ele mencionou que...

--- Bloco 2 (2026-05-21T09:30:00Z) ---
Fui ao médico. O resultado dos exames indica que...

--- Bloco 3 (2026-05-22T22:00:00Z) ---
Decidi mudar a palavra-passe de todas as contas. A nova é...
```

O atacante obteve o conteúdo completo do diário pessoal sem:

- conhecer a palavra-passe do utilizador;
- aceder diretamente à base de dados;
- quebrar AES, HMAC ou RSA;
- invalidar ou sequer tocar na cadeia de blocos.

---

## Porque é que a criptografia não protege aqui

A aplicação cifra os registos na base de dados. Essa proteção funciona contra um
atacante que consiga acesso direto ao PostgreSQL — os registos estão cifrados e as
chaves nunca são guardadas na base de dados.

Mas este ataque não passa pela base de dados. Passa pela **API**, como um utilizador
legítimo. O backend verifica o JWT, encontra a sessão em memória com as chaves
derivadas da palavra-passe, decifra os registos e devolve-os em texto limpo. É
exatamente o que faz para o utilizador real.

A cifragem protege **os dados em repouso**. Não protege contra um token comprometido.

| Proteção implementada       | O que este ataque faz                          |
|-----------------------------|------------------------------------------------|
| AES cifra os registos na BD | O backend decifra antes de devolver            |
| HMAC verifica integridade   | A integridade está intacta — não há adulteração|
| RSA assina cada bloco       | As assinaturas são válidas                     |
| Blockchain deteta remoções  | Nenhum bloco foi removido                      |
| JWT expira em 30 minutos    | O atacante tem 30 minutos para agir            |

---

## Janela de ataque

O JWT expira ao fim de 30 minutos (`ACCESS_TOKEN_EXPIRE_MINUTES = 30`). O atacante
tem essa janela para usar o token roubado. Se o utilizador fizer logout antes disso,
a sessão em memória é removida e o token deixa de funcionar imediatamente.

---

## Defesas possíveis

| Defesa                         | Efeito                                                      |
|--------------------------------|-------------------------------------------------------------|
| Guardar o token em cookie HttpOnly | JavaScript deixa de conseguir ler o token              |
| Content Security Policy (CSP)  | Limita os scripts que podem correr na página               |
| Tokens de curta duração + refresh | Reduz a janela de ataque                               |
| Logout automático por inatividade | Invalida a sessão mais cedo                            |
