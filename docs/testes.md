# Testes (pytest)

Os testes estão em `backend/tests/` e dividem-se em dois ficheiros.

Para correr todos:

```bash
cd backend
pytest
```

---

## `test_crypto_service.py` — testes unitários

Testam as funções criptográficas isoladas, sem base de dados.

| Teste | O que faz |
|---|---|
| `test_canonical_json_is_stable` | Verifica que dois dicionários com as mesmas chaves mas em ordem diferente produzem exactamente a mesma string JSON canónica. Garante que o HMAC não depende da ordem das chaves. |
| `test_aes_cbc_and_ctr_round_trip` | Cifra um payload com AES-128-CBC e com AES-128-CTR e decifra-o de seguida. Confirma que o plaintext original é recuperado em ambos os algoritmos. |
| `test_hmac_detects_tampering` | Calcula um HMAC sobre um conjunto de campos e verifica que (1) o digest é válido para os campos originais e (2) falha quando um campo é alterado (`ciphertext: "tampered"`). |

---

## `test_api_flow.py` — testes de integração

Precisam de PostgreSQL disponível; são saltados automaticamente se a base de dados não estiver acessível. Cada teste recomeça com sessões limpas.

| Teste | O que faz |
|---|---|
| `test_register_login_create_list_and_tamper_detection` | Fluxo completo: registo, tentativa de registo duplicado (409), login com password errada (401), login correcto, criação de dois registos, listagem e validação. Depois adultera directamente o `ciphertext` na BD e confirma que a API devolve `hmac: invalid`. |
| `test_authorization_is_per_user` | Cria dois utilizadores. Confirma que o segundo não vê os registos do primeiro, recebe 404 ao tentar verificar um registo alheio, e que após logout o token fica inválido (401). |
| `test_chain_detects_previous_hash_tampering` | Adultera o campo `previous_hash` do bloco 2 directamente na BD. Verifica que a API assinala `previous_hash: invalid` nesse bloco. |
| `test_chain_detects_iv_or_nonce_tampering` | Adultera o `iv_or_nonce` do bloco 1. Como o HMAC cobre esse campo, a API deve devolver `hmac: invalid`. |
| `test_chain_detects_block_hash_tampering` | Adultera o `block_hash` do bloco 1. Verifica que a API assinala `block_hash: invalid`. |
| `test_chain_detects_rsa_signature_tampering` | Adultera a `rsa_signature` do bloco 1. Verifica que a API assinala `rsa_signature: invalid`. |
| `test_chain_detects_intermediate_block_deletion` | Apaga o bloco 2 de uma cadeia com 3 blocos. O endpoint `/records/chain/status` deve devolver `chain_status: invalid` e indicar que o primeiro bloco inválido é o índice 3. |
| `test_chain_detects_last_block_deletion` | Apaga o último bloco (bloco 3) de uma cadeia com 3 blocos. Como não há bloco seguinte a apontar para ele, a deteção depende do `chain_state`: o `block_count` guardado (3) não coincide com os blocos existentes (2), por isso a API devolve `chain_status: invalid` e `chain_state.status: invalid` com `block_count_match: false`. |
| `test_system_private_key_is_stored_encrypted` | Lê directamente a tabela `system_keys` e confirma que a chave pública está em formato PEM mas a chave privada **não** aparece em plaintext — está cifrada. |
