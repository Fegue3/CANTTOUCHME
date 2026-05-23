# Demonstracao do Ataque

## Objetivo

Mostrar que um adversario com acesso directo a base de dados nao consegue remover
registos sem ser detectado pela aplicacao.

O ataque escolhido e a **remocao de um bloco intermedio**. Este e o cenario mais
forte porque:

- O bloco seguinte ao removido tem um `previous_hash` que ja nao aponta para nenhum
  bloco existente na cadeia.
- Todos os blocos a partir desse ponto ficam marcados como afectados.
- Simula o cenario real de um atacante a tentar apagar um registo comprometedor.

---

## Preparacao

Arrancar a aplicacao:

```powershell
.\setup.ps1
```

Na aplicacao (http://localhost:5173):

1. Criar uma conta em `/register`.
2. Escrever **pelo menos tres registos** em `/app`.
3. Abrir `/records` e confirmar que todos os blocos aparecem como **validos**.
4. Abrir `/chain-status` e confirmar que a cadeia esta **valida**.

---

## Executar o ataque

### 1. Ligar ao PostgreSQL dentro do container

```powershell
docker exec -it canttouchme-db psql -U canttouchme -d canttouchme
```

### 2. Ver os blocos existentes

```sql
SELECT r.block_index, r.id, u.email
FROM records r
JOIN users u ON u.id = r.user_id
ORDER BY u.email, r.block_index;
```

### 3. Apagar o bloco intermedio (bloco 2)

```sql
DELETE FROM records
WHERE block_index = 2
  AND user_id = (SELECT id FROM users WHERE email = 'email-do-utilizador@exemplo.com');
```

Substituir `email-do-utilizador@exemplo.com` pelo email usado no registo.

### 4. Sair do PostgreSQL

```sql
\q
```

---

## Resultado esperado

Voltar a aplicacao:

- Em `/records`: o bloco 3 (e seguintes) aparecem com estado `invalid_previous_hash`
  ou `chain_affected` porque o seu `previous_hash` ja nao corresponde a nenhum bloco
  existente.
- Em `/chain-status`: a cadeia aparece como **invalida**, com indicacao do primeiro
  bloco afectado.

A aplicacao detecta a remocao sem necessidade de qualquer intervencao do utilizador.

---

## Alternativas de ataque

As opcoes seguintes tambem funcionam e podem ser usadas para demonstrar validacoes
diferentes:

### Opcao A — Corromper o ciphertext de um bloco

```sql
UPDATE records
SET ciphertext = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=='
WHERE block_index = 1
  AND user_id = (SELECT id FROM users WHERE email = 'email-do-utilizador@exemplo.com');
```

Resultado: o bloco 1 aparece com `invalid_hmac` (o HMAC ja nao corresponde ao
ciphertext alterado) e possivelmente `decrypt_error`. Os blocos seguintes podem
aparecer como `chain_affected`.

### Opcao C — Falsificar o previous_hash de um bloco

```sql
UPDATE records
SET previous_hash = 'FALSIFICADO'
WHERE block_index = 2
  AND user_id = (SELECT id FROM users WHERE email = 'email-do-utilizador@exemplo.com');
```

Resultado: o bloco 2 aparece com `invalid_previous_hash` (o `previous_hash` alterado
nao corresponde ao `block_hash` do bloco 1) e `invalid_hmac` (porque o HMAC foi
calculado sobre o `previous_hash` original).

---

## O que cada validacao deteta

| Validacao              | O que detecta                                      |
|------------------------|----------------------------------------------------|
| `invalid_hmac`         | Qualquer alteracao ao ciphertext, IV, ou metadados |
| `invalid_block_hash`   | Alteracao ao hash calculado do bloco               |
| `invalid_previous_hash`| Remocao ou reordenacao de blocos                   |
| `invalid_rsa_signature`| Alteracao apos a assinatura do sistema             |
| `chain_affected`       | Blocos validos mas cujo antecessor foi corrompido  |
