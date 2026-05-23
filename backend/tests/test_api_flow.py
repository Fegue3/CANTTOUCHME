import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

os.environ["BCRYPT_COST"] = "4"
os.environ["PBKDF2_ITERATIONS"] = "1000"

from app.config import get_settings  # noqa: E402
from app.database import check_database, get_connection, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.services.session_service import clear_sessions  # noqa: E402


get_settings.cache_clear()

if check_database().status != "ok":
    pytest.skip("PostgreSQL is not available", allow_module_level=True)


@pytest.fixture()
def client() -> TestClient:
    init_db()
    clear_sessions()
    with TestClient(app) as test_client:
        yield test_client
    clear_sessions()


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid4()}@example.com"


def _register(client: TestClient, email: str, algorithm: str = "AES-128-CBC", hmac: str = "HMAC-SHA256") -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "CorrectHorse1",
            "confirm_password": "CorrectHorse1",
            "encryption_algorithm": algorithm,
            "hmac_algorithm": hmac,
        },
    )
    assert response.status_code == 201, response.text


def _login(client: TestClient, email: str) -> str:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": "CorrectHorse1"},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_register_login_create_list_and_tamper_detection(client: TestClient) -> None:
    email = _email("flow")
    _register(client, email, "AES-128-CTR", "HMAC-SHA512")

    duplicate = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "CorrectHorse1",
            "confirm_password": "CorrectHorse1",
            "encryption_algorithm": "AES-128-CBC",
            "hmac_algorithm": "HMAC-SHA256",
        },
    )
    assert duplicate.status_code == 409

    wrong_login = client.post("/auth/login", json={"email": email, "password": "wrong"})
    assert wrong_login.status_code == 401

    token = _login(client, email)
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == email

    created = client.post("/records", json={"text": "texto secreto"}, headers=headers)
    assert created.status_code == 201, created.text
    record_id = created.json()["id"]
    second = client.post("/records", json={"text": "outro segredo"}, headers=headers)
    assert second.status_code == 201, second.text

    listed = client.get("/records", headers=headers)
    assert listed.status_code == 200, listed.text
    body = listed.json()
    assert body["total"] == 2
    assert body["records"][0]["text"] == "texto secreto"
    assert body["records"][0]["validation"]["overall"] == "valid"

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ciphertext, iv_or_nonce
                FROM records
                WHERE user_id = (
                    SELECT id FROM users WHERE email = %s
                )
                ORDER BY block_index
                """,
                (email,),
            )
            rows = cursor.fetchall()
            assert len(rows) == 2
            assert "texto secreto" not in rows[0]["ciphertext"]
            assert "outro segredo" not in rows[1]["ciphertext"]
            assert rows[0]["iv_or_nonce"] != rows[1]["iv_or_nonce"]
            cursor.execute("UPDATE records SET ciphertext = %s WHERE id = %s", ("tampered", record_id))
        connection.commit()

    tampered = client.get("/records", headers=headers)
    assert tampered.status_code == 200, tampered.text
    validation = tampered.json()["records"][0]["validation"]
    assert validation["hmac"] == "invalid"
    assert validation["overall"] != "valid"


def test_authorization_is_per_user(client: TestClient) -> None:
    first_email = _email("first")
    second_email = _email("second")
    _register(client, first_email)
    _register(client, second_email)
    first_token = _login(client, first_email)
    second_token = _login(client, second_email)

    first_headers = {"Authorization": f"Bearer {first_token}"}
    second_headers = {"Authorization": f"Bearer {second_token}"}

    created = client.post("/records", json={"text": "apenas user um"}, headers=first_headers)
    assert created.status_code == 201, created.text
    record_id = created.json()["id"]

    second_list = client.get("/records", headers=second_headers)
    assert second_list.status_code == 200
    assert second_list.json()["total"] == 0

    forbidden_verify = client.get(f"/records/{record_id}/verify", headers=second_headers)
    assert forbidden_verify.status_code == 404

    logout = client.post("/auth/logout", headers=first_headers)
    assert logout.status_code == 200
    after_logout = client.get("/auth/me", headers=first_headers)
    assert after_logout.status_code == 401


def _create_user_with_three_records(client: TestClient, prefix: str) -> tuple[str, str]:
    email = _email(prefix)
    _register(client, email)
    token = _login(client, email)
    headers = {"Authorization": f"Bearer {token}"}
    for index in range(1, 4):
        response = client.post("/records", json={"text": f"registo {index}"}, headers=headers)
        assert response.status_code == 201, response.text
    baseline = client.get("/records/chain/status", headers=headers)
    assert baseline.status_code == 200
    assert baseline.json()["chain_status"] == "valid"
    return email, token


def test_chain_detects_previous_hash_tampering(client: TestClient) -> None:
    email, token = _create_user_with_three_records(client, "prev")
    headers = {"Authorization": f"Bearer {token}"}

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE records
                SET previous_hash = 'tampered'
                WHERE user_id = (SELECT id FROM users WHERE email = %s)
                  AND block_index = 2
                """,
                (email,),
            )
        connection.commit()

    response = client.get("/records", headers=headers)
    assert response.status_code == 200
    records = response.json()["records"]
    assert records[1]["validation"]["previous_hash"] == "invalid"
    assert records[1]["validation"]["overall"] == "invalid_previous_hash"


def test_chain_detects_iv_or_nonce_tampering(client: TestClient) -> None:
    email, token = _create_user_with_three_records(client, "iv")
    headers = {"Authorization": f"Bearer {token}"}

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE records
                SET iv_or_nonce = 'tampered'
                WHERE user_id = (SELECT id FROM users WHERE email = %s)
                  AND block_index = 1
                """,
                (email,),
            )
        connection.commit()

    response = client.get("/records", headers=headers)
    assert response.status_code == 200
    records = response.json()["records"]
    assert records[0]["validation"]["hmac"] == "invalid"
    assert records[0]["validation"]["overall"] == "invalid_hmac"


def test_chain_detects_block_hash_tampering(client: TestClient) -> None:
    email, token = _create_user_with_three_records(client, "hash")
    headers = {"Authorization": f"Bearer {token}"}

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE records
                SET block_hash = 'tampered'
                WHERE user_id = (SELECT id FROM users WHERE email = %s)
                  AND block_index = 1
                """,
                (email,),
            )
        connection.commit()

    response = client.get("/records", headers=headers)
    assert response.status_code == 200
    records = response.json()["records"]
    assert records[0]["validation"]["block_hash"] == "invalid"
    assert records[0]["validation"]["overall"] == "invalid_block_hash"


def test_chain_detects_rsa_signature_tampering(client: TestClient) -> None:
    email, token = _create_user_with_three_records(client, "rsa")
    headers = {"Authorization": f"Bearer {token}"}

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE records
                SET rsa_signature = 'tampered'
                WHERE user_id = (SELECT id FROM users WHERE email = %s)
                  AND block_index = 1
                """,
                (email,),
            )
        connection.commit()

    response = client.get("/records", headers=headers)
    assert response.status_code == 200
    records = response.json()["records"]
    assert records[0]["validation"]["rsa_signature"] == "invalid"
    assert records[0]["validation"]["overall"] == "invalid_rsa_signature"


def test_chain_detects_intermediate_block_deletion(client: TestClient) -> None:
    email, token = _create_user_with_three_records(client, "delete")
    headers = {"Authorization": f"Bearer {token}"}

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM records
                WHERE user_id = (SELECT id FROM users WHERE email = %s)
                  AND block_index = 2
                """,
                (email,),
            )
        connection.commit()

    response = client.get("/records/chain/status", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["chain_status"] == "invalid"
    assert body["first_invalid_block_index"] == 3


def test_chain_detects_last_block_deletion(client: TestClient) -> None:
    email, token = _create_user_with_three_records(client, "last")
    headers = {"Authorization": f"Bearer {token}"}

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM records
                WHERE user_id = (SELECT id FROM users WHERE email = %s)
                  AND block_index = 3
                """,
                (email,),
            )
        connection.commit()

    response = client.get("/records/chain/status", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["chain_status"] == "invalid"
    assert body["chain_state"]["status"] == "invalid"
    assert body["chain_state"]["block_count_match"] is False


def test_system_private_key_is_stored_encrypted(client: TestClient) -> None:
    email = _email("key")
    _register(client, email)
    _login(client, email)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT public_key, private_key_encrypted
                FROM system_keys
                WHERE active = TRUE
                ORDER BY created_at DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()

    assert row is not None
    assert "BEGIN PUBLIC KEY" in row["public_key"]
    assert "BEGIN PRIVATE KEY" not in row["private_key_encrypted"]
    assert "PRIVATE KEY" not in row["private_key_encrypted"]
