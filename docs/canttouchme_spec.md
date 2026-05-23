# CANTTOUCHME — Especificação Técnica do Projecto

## 1. Objectivo do documento

Este documento define o que vai ser implementado no projecto CANTTOUCHME.

O objectivo é ter uma especificação simples, directa e suficientemente detalhada para:

- orientar a implementação;
- servir como base para o README técnico;
- ajudar uma LLM a gerar código coerente;
- justificar as decisões tomadas durante a apresentação.

Este documento segue o enunciado do projecto 2.6 — CANTTOUCHME: Um Livro de Registos Pessoal e Seguro.

---

## 2. Ideia do projecto

O CANTTOUCHME é uma aplicação web para guardar registos pessoais de texto de forma segura e imutável.

A aplicação suporta vários utilizadores. Cada utilizador pode criar uma conta, iniciar sessão, escrever descrições sobre actividades do seu dia e consultar registos anteriores.

Os registos nunca devem ser guardados em texto limpo. Antes de serem guardados, os registos são cifrados com uma chave única por utilizador. Essa chave é derivada da palavra-passe do utilizador e de um número aleatório associado a esse utilizador.

Além da confidencialidade, a aplicação também deve garantir integridade. Para isso, cada utilizador terá uma chave de integridade própria, também derivada da sua palavra-passe e de outro número aleatório associado ao utilizador.

Cada registo terá um código de autenticação de mensagem. Os registos também serão ligados entre si ao estilo de uma blockchain local, onde cada novo bloco referencia o hash do bloco anterior.

---

## 3. Objectivos principais

O sistema deve garantir:

- registo e autenticação de utilizadores;
- separação dos dados por utilizador;
- confidencialidade dos registos;
- integridade dos registos;
- imutabilidade lógica dos registos;
- detecção de alterações indevidas na base de dados;
- validação da cadeia de blocos;
- demonstração clara das primitivas criptográficas usadas.

---

## 4. Stack tecnológica

### 4.1 Frontend

O frontend será desenvolvido com:

- React;
- TypeScript;
- Vite.

O frontend é responsável por:

- apresentar a interface;
- recolher input do utilizador;
- chamar a API do backend;
- guardar temporariamente o JWT;
- mostrar os registos e os estados de validação.

O frontend não deve implementar lógica criptográfica sensível.

### 4.2 Backend

O backend será desenvolvido em:

- Python;
- FastAPI.

O backend é responsável por:

- registo de utilizadores;
- login;
- emissão e validação de JWT;
- hash seguro das palavras-passe;
- derivação das chaves de cifra e integridade;
- cifra dos registos;
- decifra dos registos;
- cálculo e verificação de HMAC;
- criação e validação da blockchain local;
- geração e uso das chaves RSA de sistema;
- comunicação com PostgreSQL.

FastAPI foi escolhido por ser simples, legível, fácil de documentar e adequado para criar uma API REST para um frontend React.

### 4.3 Base de dados

A base de dados será:

- PostgreSQL.

A base de dados guarda:

- utilizadores;
- hashes de palavras-passe;
- salts dos utilizadores;
- escolhas criptográficas dos utilizadores;
- registos cifrados;
- HMACs;
- hashes de blocos;
- assinaturas RSA;
- âncora do estado da cadeia por utilizador (`chain_state`);
- metadados da chave RSA do sistema.

A base de dados nunca guarda:

- palavras-passe em texto limpo;
- chaves de cifra derivadas;
- chaves de integridade derivadas;
- textos dos registos em claro.

### 4.4 Docker

O projecto deve suportar Docker para facilitar a execução e a demonstração.

A configuração deve incluir:

- container do backend;
- container do frontend;
- container PostgreSQL.

O ficheiro principal será:

```text
docker-compose.yml
```

---

## 5. Funcionalidades obrigatórias do enunciado

A aplicação deve implementar obrigatoriamente as seguintes funcionalidades.

### 5.1 Registo de utilizadores

A aplicação permite que um utilizador se registe com:

- e-mail;
- palavra-passe.

A palavra-passe não é guardada em texto limpo. É guardado apenas um hash seguro da palavra-passe.

### 5.2 Chave de cifra por utilizador

A aplicação gera automaticamente uma chave de cifra/decifra para cada utilizador.

A chave é derivada a partir de:

- palavra-passe do utilizador;
- número aleatório associado ao utilizador.

Esta chave é usada para cifrar e decifrar os registos do utilizador.

### 5.3 Chave de integridade por utilizador

A aplicação gera automaticamente uma chave de integridade para cada utilizador.

A chave é derivada a partir de:

- palavra-passe do utilizador;
- outro número aleatório associado ao utilizador.

O número aleatório usado para integridade deve ser diferente do número aleatório usado para cifra.

Esta chave é usada para criar e verificar códigos de autenticação de mensagem.

### 5.4 Inserção de registos

A aplicação permite que um utilizador autenticado insira registos de texto.

Cada registo inclui:

- data do registo;
- texto introduzido pelo utilizador.

Antes de ser guardado, o registo é cifrado.

### 5.5 Cifra AES-128-CBC

A aplicação suporta AES-128-CBC.

AES-128-CBC é obrigatório porque é pedido no enunciado.

Cada registo cifrado com AES-128-CBC usa um IV aleatório único.

### 5.6 Código de autenticação de mensagem

A aplicação guarda um código de autenticação de mensagem para cada registo.

Esse código é calculado com a chave de integridade do utilizador.

O objectivo é detectar alterações indevidas aos registos guardados.

### 5.7 Consulta de registos anteriores

A aplicação permite que um utilizador veja os seus registos anteriores.

Quando o utilizador consulta registos anteriores, a aplicação:

1. obtém os registos pertencentes ao utilizador autenticado;
2. verifica a integridade dos registos;
3. decifra os registos quando possível;
4. mostra os registos ao utilizador;
5. mostra o estado de validade de cada registo.

Um utilizador não pode consultar registos de outro utilizador.

---

## 6. Funcionalidades extra que serão implementadas

Todas as funcionalidades de fortalecimento sugeridas no enunciado serão implementadas.

### 6.1 Verificação de HMAC antes de mostrar registos

Antes de mostrar registos anteriores, a aplicação verifica o código de autenticação de mensagem de cada registo.

Cada registo é apresentado com um estado:

- válido;
- não válido.

### 6.2 Escolha da cifra no registo

Durante o registo, o utilizador escolhe a cifra a usar nos seus registos.

Opções:

- AES-128-CBC;
- AES-128-CTR.

A escolha fica guardada no perfil do utilizador.

### 6.3 Escolha da função de HMAC no registo

Durante o registo, o utilizador escolhe a função de HMAC a usar.

Opções:

- HMAC-SHA256;
- HMAC-SHA512.

A escolha fica guardada no perfil do utilizador.

### 6.4 Assinaturas digitais RSA

O sistema usa assinaturas digitais RSA como mecanismo adicional de verificação.

O sistema gera um par de chaves RSA de sistema:

- chave privada RSA do sistema;
- chave pública RSA do sistema.

A chave privada é usada para assinar blocos.

A chave pública é usada para verificar assinaturas.

As assinaturas RSA não substituem o HMAC. São uma camada adicional de validação.

### 6.5 Blockchain local

A aplicação implementa uma blockchain local por utilizador.

Cada registo é um bloco.

Cada bloco referencia o hash do bloco anterior do mesmo utilizador.

A blockchain serve para detectar:

- alteração de blocos antigos;
- remoção de blocos intermédios;
- reordenação de blocos;
- tentativa de adulteração da sequência de registos;
- remoção do último bloco.

---

## 7. Decisões criptográficas

### 7.1 Hash da palavra-passe

A palavra-passe do utilizador será protegida com:

- bcrypt.

Configuração definida:

```text
bcrypt cost = 12
```

Motivo:

- bcrypt é seguro, conhecido, fácil de usar e adequado para autenticação;
- cost 12 é uma escolha equilibrada entre segurança e desempenho para um projecto académico.

O hash bcrypt é usado apenas para autenticar o utilizador.

O hash bcrypt não é usado como chave de cifra.

### 7.2 Derivação de chaves

As chaves de cifra e integridade serão derivadas com:

```text
PBKDF2-HMAC-SHA256
```

Configuração definida:

```text
Iterações: 600000
Tamanho da chave de cifra: 16 bytes / 128 bits
Tamanho da chave de integridade: 32 bytes / 256 bits
Salt de cifra: 16 bytes aleatórios
Salt de integridade: 16 bytes aleatórios
```

Motivo:

- PBKDF2 é simples de explicar;
- é adequado para derivar chaves a partir de palavras-passe;
- permite cumprir directamente o requisito do enunciado;
- usar salts diferentes garante que a chave de cifra e a chave de integridade são independentes.

### 7.3 Chave de cifra

A chave de cifra é derivada a partir de:

- palavra-passe do utilizador;
- `encryption_salt`.

A chave tem:

```text
128 bits
```

Esta chave é usada com:

- AES-128-CBC; ou
- AES-128-CTR.

### 7.4 Chave de integridade

A chave de integridade é derivada a partir de:

- palavra-passe do utilizador;
- `integrity_salt`.

A chave tem:

```text
256 bits
```

Esta chave é usada para HMAC.

### 7.5 AES-128-CBC

Quando o utilizador escolhe AES-128-CBC:

- cada registo usa um IV aleatório de 16 bytes;
- o texto a cifrar é preenchido com padding PKCS#7;
- o IV é guardado na base de dados em Base64;
- o IV não é secreto, mas nunca deve ser reutilizado com a mesma chave.

### 7.6 AES-128-CTR

Quando o utilizador escolhe AES-128-CTR:

- cada registo usa um nonce aleatório;
- o nonce é guardado na base de dados em Base64;
- o nonce não é secreto, mas nunca deve ser reutilizado com a mesma chave.

### 7.7 Conteúdo cifrado

O conteúdo cifrado deve incluir a data e o texto do registo.

Antes de cifrar, o backend cria um payload JSON canónico.

Exemplo conceptual:

```json
{
  "timestamp": "2026-05-07T14:30:00Z",
  "text": "Hoje estudei criptografia."
}
```

Este JSON é serializado de forma estável e depois cifrado.

A base de dados guarda apenas o criptograma.

A data pode existir também como metadado técnico `created_at` para paginação e ordenação, mas a data considerada parte do registo fica dentro do payload cifrado.

### 7.8 HMAC

O HMAC é calculado sobre uma representação canónica dos campos protegidos.

Campos protegidos pelo HMAC:

- `user_id`;
- `block_index`;
- `previous_hash`;
- `iv_or_nonce`;
- `ciphertext`;
- `encryption_algorithm`;
- `hmac_algorithm`.

O HMAC é calculado depois da cifra.

O HMAC protege o criptograma e os metadados necessários para validar o bloco.

### 7.9 Hash do bloco

O hash do bloco é calculado com:

```text
SHA-256
```

Campos usados no hash do bloco:

- `user_id`;
- `block_index`;
- `previous_hash`;
- `iv_or_nonce`;
- `ciphertext`;
- `hmac`;
- `encryption_algorithm`;
- `hmac_algorithm`.

O hash do bloco é guardado em Base64 ou hexadecimal.

Este hash é usado pelo bloco seguinte no campo `previous_hash`.

### 7.10 Assinatura RSA

Cada bloco é assinado pelo sistema.

Algoritmo definido:

```text
RSA-PSS com SHA-256
```

Tamanho da chave RSA:

```text
2048 bits
```

A assinatura é calculada sobre o `block_hash` e os principais metadados do bloco.

A assinatura é guardada na base de dados em Base64.

---

## 8. Gestão das chaves durante a sessão

As chaves de cifra e integridade derivam da palavra-passe do utilizador.

Como a aplicação usa JWT, é necessário manter uma associação entre o utilizador autenticado e as chaves derivadas durante a sessão.

A abordagem definida é:

1. O utilizador faz login com e-mail e palavra-passe.
2. O backend valida a palavra-passe com bcrypt.
3. Se a palavra-passe estiver correcta, o backend deriva:
   - chave de cifra;
   - chave de integridade.
4. O backend cria uma sessão interna com um `session_id` aleatório.
5. O backend guarda em memória:
   - `session_id`;
   - `user_id`;
   - chave de cifra;
   - chave de integridade;
   - data de expiração.
6. O JWT inclui o `user_id` e o `session_id`.
7. Em cada pedido autenticado, o backend valida o JWT e procura as chaves em memória usando o `session_id`.
8. Quando o utilizador faz logout ou a sessão expira, as chaves são removidas da memória.

Configuração definida:

```text
Tempo de expiração do JWT: 30 minutos
Tempo de expiração das chaves em memória: 30 minutos
Renovação automática: não na primeira versão
```

Se o backend reiniciar, as sessões em memória perdem-se. Nesse caso, o utilizador terá de fazer login novamente.

As chaves derivadas nunca são guardadas na base de dados.

---

## 9. Blockchain local

### 9.1 Modelo

Cada utilizador tem a sua própria cadeia de blocos.

Não existe uma blockchain global.

Motivo:

- os registos são pessoais;
- cada utilizador tem as suas próprias chaves;
- a integridade deve ser validada por utilizador;
- isto segue melhor a ideia de livro de registos pessoal.

### 9.2 Bloco génesis

O primeiro bloco de cada utilizador usa um valor inicial fixo no campo `previous_hash`.

Valor definido:

```text
GENESIS
```

Este valor indica que o bloco não tem bloco anterior.

### 9.3 Estrutura conceptual de um bloco

Segundo o enunciado, cada bloco contém:

- valor hash do bloco anterior;
- data do registo;
- texto do registo;
- código de autenticação de mensagem.

Na implementação, como os registos têm de ser cifrados, a estrutura persistida será:

- `previous_hash`;
- data e texto dentro do payload cifrado;
- `iv_or_nonce`;
- `ciphertext`;
- `hmac`;
- `block_hash`;
- `rsa_signature`.

### 9.4 Criação de um bloco

Quando o utilizador cria um registo, o backend:

1. identifica o utilizador autenticado;
2. obtém as chaves da sessão;
3. procura o último bloco do utilizador;
4. define o `previous_hash`;
5. define o novo `block_index`;
6. cria o payload com data e texto;
7. cifra o payload;
8. calcula o HMAC;
9. calcula o hash do bloco;
10. assina o bloco com RSA;
11. guarda o bloco na base de dados;
12. actualiza a âncora `chain_state` com o novo `block_hash` e `block_count`, assinada com RSA, **na mesma transacção atómica**.

### 9.5 Validação da cadeia

Para validar a cadeia, o backend percorre os blocos do utilizador por ordem de `block_index`.

Para cada bloco, valida:

1. se o `previous_hash` corresponde ao `block_hash` do bloco anterior;
2. se o HMAC está correcto;
3. se o `block_hash` recalculado corresponde ao guardado;
4. se a assinatura RSA é válida;
5. se o conteúdo pode ser decifrado.

No final, o endpoint `GET /records/chain/status` valida também a âncora `chain_state`:

6. se o `block_count` guardado na âncora coincide com o número de blocos existentes na base de dados;
7. se o `last_hash` guardado na âncora coincide com o `block_hash` do último bloco;
8. se a assinatura RSA da âncora é válida.

Se qualquer um dos pontos 6, 7 ou 8 falhar, o `chain_status` é marcado como `invalid`.

### 9.6 Âncora do estado da cadeia (`chain_state`)

A blockchain encadeada apenas detecta remoção de blocos quando existe um bloco seguinte que referencia o removido. O último bloco da cadeia não tem bloco seguinte, pelo que a sua remoção seria indetectável sem um mecanismo adicional.

Para colmatar esta lacuna, o sistema mantém uma âncora por utilizador com o seguinte conteúdo:

- `last_hash` — `block_hash` do bloco mais recente;
- `block_count` — número total de blocos;
- `rsa_signature` — assinatura RSA-PSS sobre `{user_id, last_hash, block_count}`.

A âncora é actualizada em cada inserção de bloco, na mesma transacção atómica. Se um atacante apagar o último bloco, o `block_count` guardado na âncora fica a não coincidir com o número real de blocos na base de dados. Como a assinatura RSA da âncora foi calculada com a chave privada do sistema, o atacante não consegue forjar uma âncora válida com o novo `block_count`.

### 9.6 Estados de validação

Cada bloco pode ter os seguintes estados:

- `valid`;
- `invalid_hmac`;
- `invalid_block_hash`;
- `invalid_previous_hash`;
- `invalid_rsa_signature`;
- `decrypt_error`;
- `chain_affected`.

O estado geral do bloco é `valid` apenas se todas as validações passarem.

Se um bloco antigo for alterado ou apagado, os blocos seguintes podem ser marcados como `chain_affected`.

---

## 10. Modelo de dados

### 10.1 Tabela `users`

Guarda os utilizadores e os parâmetros criptográficos associados.

Campos:

```text
id UUID PRIMARY KEY
email VARCHAR UNIQUE NOT NULL
password_hash TEXT NOT NULL
encryption_salt TEXT NOT NULL
integrity_salt TEXT NOT NULL
encryption_algorithm VARCHAR NOT NULL
hmac_algorithm VARCHAR NOT NULL
created_at TIMESTAMP NOT NULL
```

Valores permitidos para `encryption_algorithm`:

```text
AES-128-CBC
AES-128-CTR
```

Valores permitidos para `hmac_algorithm`:

```text
HMAC-SHA256
HMAC-SHA512
```

### 10.2 Tabela `records`

Guarda os blocos/registos cifrados.

Campos:

```text
id UUID PRIMARY KEY
user_id UUID NOT NULL REFERENCES users(id)
block_index INTEGER NOT NULL
previous_hash TEXT NOT NULL
iv_or_nonce TEXT NOT NULL
ciphertext TEXT NOT NULL
hmac TEXT NOT NULL
block_hash TEXT NOT NULL
rsa_signature TEXT NOT NULL
created_at TIMESTAMP NOT NULL
```

Restrições:

```text
UNIQUE(user_id, block_index)
```

O campo `ciphertext` é guardado em Base64.

O campo `iv_or_nonce` é guardado em Base64.

O campo `hmac` é guardado em Base64.

O campo `rsa_signature` é guardado em Base64.

O campo `block_hash` pode ser guardado em hexadecimal.

### 10.3 Tabela `chain_state`

Guarda a âncora do estado da cadeia por utilizador.

Campos:

```text
user_id UUID PRIMARY KEY REFERENCES users(id)
last_hash TEXT NOT NULL
block_count INTEGER NOT NULL
rsa_signature TEXT NOT NULL
updated_at TIMESTAMP NOT NULL
```

Existe no máximo uma linha por utilizador.

A linha é criada ou actualizada em cada `POST /records`, na mesma transacção que insere o bloco.

A `rsa_signature` cobre os campos `{user_id, last_hash, block_count}`.

### 10.4 Tabela `system_keys`

Guarda informação sobre as chaves RSA do sistema.

Campos:

```text
id UUID PRIMARY KEY
public_key TEXT NOT NULL
private_key_encrypted TEXT NOT NULL
created_at TIMESTAMP NOT NULL
active BOOLEAN NOT NULL
```

A chave privada RSA é cifrada antes de ser guardada.

A chave usada para cifrar a chave privada RSA vem de uma variável de ambiente do backend.

Nome definido:

```text
SYSTEM_RSA_KEY_ENCRYPTION_SECRET
```

Em ambiente de desenvolvimento, se não existir chave RSA activa, o backend gera uma automaticamente.

---

## 11. API do backend

A API será REST.

Todas as respostas devem ser JSON.

### 11.1 `POST /auth/register`

Regista um novo utilizador.

Recebe:

```json
{
  "email": "user@example.com",
  "password": "password",
  "confirm_password": "password",
  "encryption_algorithm": "AES-128-CBC",
  "hmac_algorithm": "HMAC-SHA256"
}
```

Faz:

1. valida input;
2. verifica se o e-mail já existe;
3. gera `encryption_salt`;
4. gera `integrity_salt`;
5. gera hash bcrypt da palavra-passe;
6. guarda o utilizador.

Devolve:

```json
{
  "message": "User registered successfully"
}
```

### 11.2 `POST /auth/login`

Autentica um utilizador.

Recebe:

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

Faz:

1. procura o utilizador;
2. valida a palavra-passe com bcrypt;
3. deriva as chaves;
4. cria sessão em memória;
5. gera JWT.

Devolve:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "email": "user@example.com",
    "encryption_algorithm": "AES-128-CBC",
    "hmac_algorithm": "HMAC-SHA256"
  }
}
```

### 11.3 `POST /auth/logout`

Termina a sessão.

Requer JWT.

Faz:

1. obtém o `session_id` do JWT;
2. remove as chaves em memória;
3. termina a sessão.

### 11.4 `GET /auth/me`

Devolve dados básicos do utilizador autenticado.

Não devolve:

- palavra-passe;
- salts;
- chaves;
- hashes internos.

### 11.5 `POST /records`

Cria um novo registo.

Requer JWT.

Recebe:

```json
{
  "text": "Hoje estudei criptografia."
}
```

Faz:

1. valida sessão;
2. obtém chaves da sessão;
3. cria o bloco;
4. cifra o payload;
5. calcula HMAC;
6. calcula hash do bloco;
7. assina com RSA;
8. guarda na base de dados.

Devolve:

```json
{
  "id": "record-id",
  "block_index": 1,
  "message": "Record created successfully"
}
```

### 11.6 `GET /records`

Lista registos do utilizador autenticado.

Requer JWT.

Parâmetros opcionais:

```text
page
page_size
start_date
end_date
status
```

Valores definidos:

```text
page_size default = 10
page_size máximo = 50
```

Devolve:

```json
{
  "page": 1,
  "page_size": 10,
  "total": 3,
  "records": [
    {
      "id": "record-id",
      "block_index": 1,
      "timestamp": "2026-05-07T14:30:00Z",
      "text": "Hoje estudei criptografia.",
      "validation": {
        "hmac": "valid",
        "block_hash": "valid",
        "previous_hash": "valid",
        "rsa_signature": "valid",
        "overall": "valid"
      }
    }
  ]
}
```

### 11.7 `GET /records/chain/status`

Mostra o estado geral da cadeia do utilizador autenticado.

Requer JWT.

Devolve:

```json
{
  "total_blocks": 3,
  "valid_blocks": 3,
  "invalid_blocks": 0,
  "first_invalid_block_index": null,
  "chain_status": "valid",
  "chain_state": {
    "status": "valid",
    "block_count_match": true,
    "last_hash_match": true,
    "signature": "valid"
  }
}
```

O campo `chain_status` é `"invalid"` se qualquer bloco for inválido **ou** se a âncora `chain_state` não for válida.

O campo `chain_state.status` pode ser:

- `valid` — âncora presente e consistente;
- `invalid` — âncora presente mas inconsistente (deleção do último bloco, adulteração da âncora);
- `missing` — âncora ausente apesar de existirem blocos.

### 11.8 `GET /records/{id}/verify`

Verifica um registo específico.

Requer JWT.

Devolve:

```json
{
  "record_id": "record-id",
  "block_index": 1,
  "validation": {
    "hmac": "valid",
    "block_hash": "valid",
    "previous_hash": "valid",
    "rsa_signature": "valid",
    "decrypt": "valid",
    "overall": "valid"
  }
}
```

---

## 12. Interface da aplicação

A aplicação não precisa de landing page.

### 12.1 Páginas

A aplicação terá:

```text
/register
/login
/app
/records
/chain-status
```

### 12.2 Página de registo

Campos:

- e-mail;
- palavra-passe;
- confirmação da palavra-passe;
- escolha da cifra;
- escolha da função de HMAC.

### 12.3 Página de login

Campos:

- e-mail;
- palavra-passe.

Após login, o utilizador vai para:

```text
/app
```

### 12.4 Página principal

A página principal deve ser simples.

Deve mostrar:

- caixa de texto para novo registo;
- botão para guardar;
- ligação para registos anteriores;
- ligação para estado da cadeia;
- informação curta sobre cifra e HMAC escolhidos.

### 12.5 Página de registos

Mostra registos anteriores de forma paginada.

Cada registo mostra:

- data;
- texto decifrado;
- índice do bloco;
- estado de HMAC;
- estado do hash do bloco;
- estado da assinatura RSA;
- estado geral.

Filtros definidos:

- data inicial;
- data final;
- estado: todos, válidos, inválidos.

### 12.6 Página de estado da cadeia

Mostra:

- total de blocos;
- blocos válidos;
- blocos inválidos;
- primeiro bloco inválido;
- estado geral da cadeia.

---

## 13. Fluxos principais

### 13.1 Registo

1. Utilizador abre `/register`.
2. Introduz e-mail e palavra-passe.
3. Escolhe cifra.
4. Escolhe HMAC.
5. Backend cria salts.
6. Backend cria hash bcrypt.
7. Backend guarda utilizador.

### 13.2 Login

1. Utilizador abre `/login`.
2. Introduz e-mail e palavra-passe.
3. Backend valida bcrypt.
4. Backend deriva chaves.
5. Backend cria sessão em memória.
6. Backend devolve JWT.
7. Frontend redirecciona para `/app`.

### 13.3 Criar registo

1. Utilizador escreve texto.
2. Frontend envia texto para `POST /records`.
3. Backend cria payload com data e texto.
4. Backend cifra payload.
5. Backend calcula HMAC.
6. Backend calcula hash do bloco.
7. Backend assina o bloco.
8. Backend guarda o bloco.

### 13.4 Consultar registos

1. Utilizador abre `/records`.
2. Frontend chama `GET /records`.
3. Backend valida a cadeia.
4. Backend verifica HMACs.
5. Backend verifica assinaturas RSA.
6. Backend decifra os registos possíveis.
7. Frontend mostra registos e estados.

### 13.5 Validar cadeia

1. Utilizador abre `/chain-status`.
2. Backend percorre blocos por ordem.
3. Backend valida `previous_hash`, HMAC, hash do bloco e assinatura RSA.
4. Frontend mostra resumo.

---

## 14. Regras de segurança

A implementação deve seguir estas regras:

1. Nunca guardar palavras-passe em texto limpo.
2. Nunca guardar registos em texto limpo.
3. Nunca guardar chaves derivadas na base de dados.
4. Usar salt de cifra e salt de integridade diferentes.
5. Usar IV/nonce novo por registo.
6. Nunca reutilizar IV/nonce com a mesma chave.
7. Validar HMAC antes de confiar nos dados.
8. Validar assinatura RSA antes de considerar o bloco totalmente válido.
9. Não permitir acesso a registos de outros utilizadores.
10. Não permitir edição de registos.
11. Não permitir eliminação normal de registos pela aplicação.
12. Se um bloco antigo for alterado, a cadeia deve ficar inválida.
13. O JWT não pode conter dados sensíveis.
14. As chaves derivadas só podem existir em memória e temporariamente.
15. Mensagens de erro não devem revelar informação sensível.
16. A chave privada RSA não pode estar em texto limpo na base de dados.
17. A aplicação deve rejeitar pedidos autenticados se a sessão em memória já tiver expirado.

---

## 15. Testes

### 15.1 Autenticação

- registar utilizador válido;
- impedir e-mail repetido;
- login correcto;
- login com palavra-passe errada;
- acesso sem JWT;
- logout remove sessão.

### 15.2 Cifra

- criar registo com AES-128-CBC;
- criar registo com AES-128-CTR;
- confirmar que texto não aparece em claro na base de dados;
- confirmar que registo é decifrado correctamente;
- confirmar que IV/nonce muda entre registos.

### 15.3 HMAC

- criar registo com HMAC-SHA256;
- criar registo com HMAC-SHA512;
- validar HMAC correcto;
- alterar `ciphertext` e confirmar HMAC inválido;
- alterar `iv_or_nonce` e confirmar HMAC inválido.

### 15.4 Blockchain

- criar vários registos e validar cadeia;
- alterar `previous_hash`;
- alterar `block_hash`;
- alterar `iv_or_nonce`;
- alterar `rsa_signature`;
- apagar bloco intermédio directamente na base de dados;
- apagar o último bloco directamente na base de dados;
- confirmar que a cadeia fica inválida em todos os casos acima.

### 15.5 RSA

- gerar chave RSA de sistema;
- assinar bloco;
- verificar assinatura válida;
- alterar bloco e confirmar assinatura inválida.

### 15.6 Autorização

- criar dois utilizadores;
- criar registos para ambos;
- confirmar que um utilizador não vê registos do outro;
- tentar aceder directamente a um registo de outro utilizador.

### 15.7 Interface

- registo;
- login;
- criação de registo;
- consulta paginada;
- filtros por data;
- filtro por estado;
- visualização do estado da cadeia.

---

## 16. Ataque para a apresentação

O ataque escolhido será a alteração ou remoção manual de um bloco antigo na base de dados.

### 16.1 Objectivo

Mostrar que um atacante com acesso directo à base de dados não consegue alterar registos sem ser detectado.

### 16.2 Passos

1. Criar um utilizador.
2. Criar pelo menos três registos.
3. Mostrar que todos os registos estão válidos.
4. Abrir a base de dados PostgreSQL.
5. Alterar manualmente um campo de um bloco antigo, por exemplo:
   - `ciphertext`;
   - `previous_hash`;
   - `hmac`;
   - `block_hash`.
6. Em alternativa, apagar um bloco intermédio.
7. Voltar à aplicação.
8. Consultar os registos.
9. Mostrar que o sistema detecta a alteração.
10. Explicar que a validação falha por HMAC, hash, assinatura RSA ou quebra da cadeia.

### 16.3 Resultado esperado

O bloco alterado deve aparecer como inválido.

Se a cadeia for quebrada, os blocos seguintes devem aparecer como afectados.

---

## 17. Critérios de aceitação

O projecto é considerado completo se cumprir todos estes pontos:

### 17.1 Requisitos obrigatórios

- [ ] A aplicação permite registo com e-mail e palavra-passe.
- [ ] A palavra-passe é guardada como hash seguro.
- [ ] A aplicação gera uma chave de cifra derivada da palavra-passe e de um número aleatório do utilizador.
- [ ] A aplicação gera uma chave de integridade derivada da palavra-passe e de outro número aleatório do utilizador.
- [ ] A aplicação permite criar registos de texto.
- [ ] Os registos são cifrados com AES-128-CBC quando essa cifra é escolhida.
- [ ] A aplicação guarda HMAC para cada registo.
- [ ] A aplicação permite consultar registos anteriores.
- [ ] Os registos pertencem apenas ao utilizador autenticado.

### 17.2 Funcionalidades extra

- [ ] A aplicação verifica HMAC antes de mostrar o estado dos registos.
- [ ] A aplicação mostra se cada registo é válido ou não válido.
- [ ] A aplicação permite escolher AES-128-CBC ou AES-128-CTR no registo.
- [ ] A aplicação permite escolher HMAC-SHA256 ou HMAC-SHA512 no registo.
- [ ] A aplicação usa assinaturas digitais RSA de sistema.
- [ ] A aplicação implementa blockchain local de registos.

### 17.3 Engenharia e entrega

- [ ] O backend corre correctamente.
- [ ] O frontend corre correctamente.
- [ ] A base de dados corre correctamente.
- [ ] O projecto pode ser executado com Docker.
- [ ] Existe README com instruções.
- [ ] Existem testes relevantes.
- [ ] Existe demonstração do ataque.
- [ ] A aplicação está funcional no final do semestre.

---

## 18. Estrutura do projecto

Estrutura sugerida:

```text
canttouchme/
  backend/
    app/
      main.py
      config.py
      database.py
      models/
        user.py
        record.py
        system_key.py
      schemas/
        auth.py
        record.py
      routes/
        auth.py
        records.py
      services/
        auth_service.py
        crypto_service.py
        record_service.py
        blockchain_service.py
        rsa_service.py
        session_service.py
      utils/
        canonical_json.py
    tests/
    requirements.txt
    Dockerfile

  frontend/
    src/
      api/
        authApi.ts
        recordsApi.ts
      components/
      pages/
        LoginPage.tsx
        RegisterPage.tsx
        AppPage.tsx
        RecordsPage.tsx
        ChainStatusPage.tsx
      types/
      main.tsx
    package.json
    Dockerfile

  docs/
    CANTTOUCHME_SPEC.md

  docker-compose.yml
  README.md
```

---

## 19. Ordem de implementação

### Fase 1 — Infraestrutura

- criar repositório;
- configurar FastAPI;
- configurar React + Vite;
- configurar PostgreSQL;
- configurar Docker Compose.

### Fase 2 — Utilizadores

- criar tabela `users`;
- implementar registo;
- implementar bcrypt;
- implementar login;
- implementar JWT;
- implementar sessões em memória.

### Fase 3 — Criptografia base

- gerar salts;
- derivar chave de cifra;
- derivar chave de integridade;
- implementar AES-128-CBC;
- implementar HMAC-SHA256.

### Fase 4 — Registos

- criar tabela `records`;
- criar registo cifrado;
- consultar e decifrar registos;
- confirmar que nada fica em texto limpo.

### Fase 5 — Extras de cifra e HMAC

- implementar AES-128-CTR;
- implementar HMAC-SHA512;
- usar as escolhas feitas no registo.

### Fase 6 — Blockchain

- implementar `previous_hash`;
- implementar `block_hash`;
- validar cadeia;
- mostrar estado da cadeia.

### Fase 7 — RSA

- gerar par de chaves RSA;
- guardar chave privada cifrada;
- assinar blocos;
- verificar assinaturas.

### Fase 8 — Interface final

- melhorar páginas;
- adicionar paginação;
- adicionar filtros;
- mostrar estados de validação.

### Fase 9 — Testes e apresentação

- escrever testes;
- preparar demo de ataque;
- escrever README;
- preparar slides.

---

## 20. Decisões finais fechadas

Estas decisões ficam fechadas para evitar ambiguidades durante a implementação.

```text
Nome do projecto: CANTTOUCHME
Tipo de aplicação: Web
Frontend: React + TypeScript + Vite
Backend: Python + FastAPI
Base de dados: PostgreSQL
Autenticação: JWT com session_id
Sessões: em memória no backend
Expiração do JWT: 30 minutos
Expiração das chaves em memória: 30 minutos
Password hash: bcrypt cost 12
Derivação de chaves: PBKDF2-HMAC-SHA256
Iterações PBKDF2: 600000
Chave de cifra: 128 bits
Chave de integridade: 256 bits
Salt de cifra: 16 bytes aleatórios
Salt de integridade: 16 bytes aleatórios
Cifras: AES-128-CBC e AES-128-CTR
HMAC: HMAC-SHA256 e HMAC-SHA512
Hash dos blocos: SHA-256
RSA: RSA-PSS com SHA-256
Tamanho RSA: 2048 bits
Armazenamento binário: Base64 em campos TEXT
Blockchain: uma cadeia por utilizador
Bloco génesis: previous_hash = GENESIS
Paginação default: 10 registos
Paginação máxima: 50 registos
Filtros: data inicial, data final, estado
Apagar registos pela aplicação: não permitido
Editar registos pela aplicação: não permitido
Ataque da apresentação: alterar ou apagar bloco antigo na base de dados
```

---

## 21. Verificação final contra o enunciado

### Obrigatório

O enunciado pede registo com e-mail e palavra-passe.

Implementado em:

- `POST /auth/register`;
- tabela `users`;
- bcrypt.

O enunciado pede representação segura da palavra-passe.

Implementado com:

- bcrypt cost 12.

O enunciado pede chave de cifra derivada da palavra-passe e de um número aleatório.

Implementado com:

- PBKDF2-HMAC-SHA256;
- `encryption_salt`;
- chave AES-128.

O enunciado pede chave de integridade derivada da palavra-passe e de outro número aleatório.

Implementado com:

- PBKDF2-HMAC-SHA256;
- `integrity_salt`;
- chave de integridade independente.

O enunciado pede inserção de registos.

Implementado com:

- `POST /records`;
- página `/app`.

O enunciado pede cifra dos registos com AES-128-CBC.

Implementado com:

- AES-128-CBC;
- IV aleatório por registo.

O enunciado pede HMAC por registo.

Implementado com:

- HMAC-SHA256 ou HMAC-SHA512;
- chave de integridade por utilizador.

O enunciado pede consulta de registos anteriores.

Implementado com:

- `GET /records`;
- página `/records`.

### Fortalecimento

O enunciado sugere verificar HMAC antes de mostrar registos e mostrar válido/não válido.

Implementado com:

- validação por registo;
- estados de validação no frontend.

O enunciado sugere escolha entre AES-128-CBC e AES-128-CTR.

Implementado no registo.

O enunciado sugere escolha entre HMAC-SHA256 e HMAC-SHA512.

Implementado no registo.

O enunciado sugere assinaturas digitais RSA de sistema.

Implementado com:

- par de chaves RSA do sistema;
- assinatura RSA-PSS por bloco.

O enunciado sugere blockchain.

Implementado com:

- uma cadeia por utilizador;
- `previous_hash`;
- `block_hash`;
- validação da cadeia.

O enunciado pede pensar num ataque para a apresentação.

Implementado com:

- ataque de alteração ou remoção manual de bloco antigo na base de dados.

## 22. Entrega no Moodle

A entrega será feita exclusivamente através do Moodle até às 23:59 do dia 31/05/2026.

Cada ficheiro submetido não pode ultrapassar 10 MB.

A entrega deve incluir:

- código da aplicação;
- scripts de instalação ou execução;
- README com instruções;
- ficheiro `.env.example`;
- documentação técnica;
- diagrama do sistema;
- diagrama do ataque;
- testes ou instruções para correr testes;
- artefactos que provem autoria e originalidade do trabalho.

Como a aplicação é web, não será entregue um executável `.exe`. Em vez disso, serão entregues scripts de execução, Dockerfile e `docker-compose.yml`.

O ficheiro principal da entrega será um `.zip` com o seguinte formato:

```text
T6-Nome1-Nome2-Nome3-Nome4-Nome5.zip

## 23. Checklist final de entrega

- [ ] O ficheiro `.zip` tem menos de 10 MB.
- [ ] O nome do ficheiro segue a nomenclatura pedida.
- [ ] O código está incluído.
- [ ] O README explica como correr o projecto.
- [ ] O `docker-compose.yml` está incluído.
- [ ] O `.env.example` está incluído.
- [ ] O diagrama de sistema está incluído.
- [ ] O diagrama de ataque está incluído.
- [ ] A especificação técnica está incluída.
- [ ] Os testes ou instruções de teste estão incluídos.
- [ ] Não foram incluídas dependências pesadas como `node_modules` ou `.venv`.
- [ ] A aplicação foi testada antes de compactar.

Conclusão: esta especificação cobre todos os requisitos obrigatórios e todos os requisitos de fortalecimento indicados no enunciado.



