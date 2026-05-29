# Cryptographic helpers for key derivation, encryption and integrity data.

from __future__ import annotations

import base64
import hashlib
import hmac as hmac_lib
import os
from typing import Any, Literal

from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import get_settings
from app.utils.canonical_json import canonical_json_bytes


EncryptionAlgorithm = Literal["AES-128-CBC", "AES-128-CTR"]
HmacAlgorithm = Literal["HMAC-SHA256", "HMAC-SHA512"]


def random_b64(length: int = 16) -> str:
    # Generate random bytes and encode them as base64 text.
    return base64.b64encode(os.urandom(length)).decode("ascii")


def b64encode_bytes(value: bytes) -> str:
    # Encode raw bytes as ASCII base64 text.
    return base64.b64encode(value).decode("ascii")


def b64decode_text(value: str) -> bytes:
    # Decode a strict ASCII base64 string back into bytes.
    return base64.b64decode(value.encode("ascii"), validate=True)


def derive_key(password: str, salt_b64: str, length: int) -> bytes:
    # Derive a PBKDF2 key of the requested length from a password and salt.
    settings = get_settings()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=b64decode_text(salt_b64),
        iterations=settings.pbkdf2_iterations,
    )
    return kdf.derive(password.encode("utf-8"))


def derive_user_keys(password: str, encryption_salt: str, integrity_salt: str) -> tuple[bytes, bytes]:
    # Derive the separate encryption and integrity keys for a user session.
    return (
        derive_key(password, encryption_salt, 16),
        derive_key(password, integrity_salt, 32),
    )


def encrypt_payload(plaintext: bytes, key: bytes, algorithm: EncryptionAlgorithm) -> tuple[str, str]:
    # Encrypt a payload with the selected AES mode and return base64 fields.
    iv_or_nonce = os.urandom(16)

    if algorithm == "AES-128-CBC":
        padder = padding.PKCS7(128).padder()
        padded = padder.update(plaintext) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv_or_nonce))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()
    elif algorithm == "AES-128-CTR":
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv_or_nonce))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    else:
        raise ValueError("Unsupported encryption algorithm")

    return b64encode_bytes(iv_or_nonce), b64encode_bytes(ciphertext)


def decrypt_payload(
    ciphertext_b64: str,
    iv_or_nonce_b64: str,
    key: bytes,
    algorithm: EncryptionAlgorithm,
) -> bytes:
    # Decrypt a payload encoded by encrypt_payload.
    iv_or_nonce = b64decode_text(iv_or_nonce_b64)
    ciphertext = b64decode_text(ciphertext_b64)

    if algorithm == "AES-128-CBC":
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv_or_nonce))
        decryptor = cipher.decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded) + unpadder.finalize()

    if algorithm == "AES-128-CTR":
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv_or_nonce))
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

    raise ValueError("Unsupported encryption algorithm")


def compute_hmac(key: bytes, algorithm: HmacAlgorithm, fields: dict[str, Any]) -> str:
    # Compute a canonical HMAC over the supplied field dictionary.
    digestmod = hashlib.sha256 if algorithm == "HMAC-SHA256" else hashlib.sha512
    digest = hmac_lib.new(key, canonical_json_bytes(fields), digestmod).digest()
    return b64encode_bytes(digest)


def verify_hmac(key: bytes, algorithm: HmacAlgorithm, fields: dict[str, Any], expected_b64: str) -> bool:
    # Compare the computed HMAC with the expected value in constant time.
    try:
        actual = compute_hmac(key, algorithm, fields)
        return hmac_lib.compare_digest(actual, expected_b64)
    except Exception:
        return False


def compute_block_hash(fields: dict[str, Any]) -> str:
    # Compute the SHA-256 hash used to link blockchain-like records.
    return hashlib.sha256(canonical_json_bytes(fields)).hexdigest()
