# Unit tests for the canonical JSON and crypto helper functions.

import json

from app.config import get_settings
from app.services import crypto_service
from app.utils.canonical_json import canonical_json_dumps


def test_canonical_json_is_stable() -> None:
    # Confirm canonical JSON output is independent of key ordering.
    left = {"text": "abc", "timestamp": "2026-05-07T14:30:00Z"}
    right = {"timestamp": "2026-05-07T14:30:00Z", "text": "abc"}

    assert canonical_json_dumps(left) == canonical_json_dumps(right)


def test_aes_cbc_and_ctr_round_trip(monkeypatch) -> None:
    # Confirm both supported AES modes can encrypt and decrypt correctly.
    monkeypatch.setenv("PBKDF2_ITERATIONS", "1000")
    get_settings.cache_clear()

    password = "CorrectHorse1"
    encryption_salt = crypto_service.random_b64(16)
    integrity_salt = crypto_service.random_b64(16)
    encryption_key, _ = crypto_service.derive_user_keys(password, encryption_salt, integrity_salt)
    payload = json.dumps({"timestamp": "2026-05-07T14:30:00Z", "text": "segredo"}).encode()

    for algorithm in ("AES-128-CBC", "AES-128-CTR"):
        iv_or_nonce, ciphertext = crypto_service.encrypt_payload(payload, encryption_key, algorithm)
        decrypted = crypto_service.decrypt_payload(ciphertext, iv_or_nonce, encryption_key, algorithm)
        assert decrypted == payload


def test_hmac_detects_tampering(monkeypatch) -> None:
    # Confirm the HMAC helper rejects mutated protected fields.
    monkeypatch.setenv("PBKDF2_ITERATIONS", "1000")
    get_settings.cache_clear()

    _, integrity_key = crypto_service.derive_user_keys(
        "CorrectHorse1",
        crypto_service.random_b64(16),
        crypto_service.random_b64(16),
    )
    fields = {
        "user_id": "u1",
        "block_index": 1,
        "previous_hash": "GENESIS",
        "iv_or_nonce": "abc",
        "ciphertext": "def",
        "encryption_algorithm": "AES-128-CBC",
        "hmac_algorithm": "HMAC-SHA256",
    }
    digest = crypto_service.compute_hmac(integrity_key, "HMAC-SHA256", fields)

    assert crypto_service.verify_hmac(integrity_key, "HMAC-SHA256", fields, digest)
    assert not crypto_service.verify_hmac(
        integrity_key,
        "HMAC-SHA256",
        {**fields, "ciphertext": "tampered"},
        digest,
    )
