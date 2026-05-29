# RSA key management and signature helpers for chain state verification.

from __future__ import annotations

import base64
import hashlib
from uuid import uuid4

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding, rsa

from app.config import get_settings
from app.database import get_connection
from app.utils.canonical_json import canonical_json_bytes


def _fernet() -> Fernet:
    # Build the deterministic Fernet instance used to wrap the private key.
    settings = get_settings()
    digest = hashlib.sha256(settings.system_rsa_key_encryption_secret.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def ensure_active_system_key() -> None:
    # Create an active RSA key pair if the database does not have one yet.
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM system_keys WHERE active = TRUE LIMIT 1")
            existing = cursor.fetchone()
            if existing:
                return

            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            public_key = private_key.public_key()
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            encrypted_private_key = _fernet().encrypt(private_pem).decode("ascii")
            cursor.execute(
                """
                INSERT INTO system_keys (id, public_key, private_key_encrypted, active)
                VALUES (%s, %s, %s, TRUE)
                """,
                (uuid4(), public_pem.decode("ascii"), encrypted_private_key),
            )
        connection.commit()


def _load_active_private_key() -> rsa.RSAPrivateKey:
    # Ensures an active system key exists (this may create a new
    # keypair in the DB). Reads the encrypted PEM from `system_keys`,
    # decrypts it using the deterministic Fernet instance derived from the
    # `system_rsa_key_encryption_secret`, and returns a `RSAPrivateKey` object.
    # Raises a RuntimeError if no key is found or the PEM does not decode to
    # an RSA private key.
    ensure_active_system_key()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT private_key_encrypted
                FROM system_keys
                WHERE active = TRUE
                ORDER BY created_at DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()

    if row is None:
        raise RuntimeError("No active RSA system key found")

    private_pem = _fernet().decrypt(row["private_key_encrypted"].encode("ascii"))
    private_key = serialization.load_pem_private_key(private_pem, password=None)

    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise RuntimeError("Invalid RSA private key type")

    return private_key


def _load_active_public_key() -> rsa.RSAPublicKey:
    # Ensures an active system key exists, reads the public PEM
    # from the DB and deserialises it to an `RSAPublicKey`. This is used for
    # runtime verification of chain-state and block signatures.
    ensure_active_system_key()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT public_key
                FROM system_keys
                WHERE active = TRUE
                ORDER BY created_at DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()

    if row is None:
        raise RuntimeError("No active RSA system key found")

    public_key = serialization.load_pem_public_key(row["public_key"].encode("ascii"))

    if not isinstance(public_key, rsa.RSAPublicKey):
        raise RuntimeError("Invalid RSA public key type")

    return public_key


def signature_fields(user_id: str, block_index: int, previous_hash: str, block_hash: str) -> dict[str, str | int]:
    # Return the canonical fields covered by a block signature.
    return {
        "user_id": user_id,
        "block_index": block_index,
        "previous_hash": previous_hash,
        "block_hash": block_hash,
    }


def chain_state_fields(user_id: str, last_hash: str, block_count: int) -> dict[str, str | int]:
    # Return the canonical fields covered by the chain-state signature.
    return {
        "user_id": user_id,
        "last_hash": last_hash,
        "block_count": block_count,
    }


def sign_block(fields: dict[str, str | int]) -> str:
    # Loads the active private key and signs the canonical JSON
    # bytes using RSA-PSS (MGF1 + SHA256). The signature is base64 encoded
    # for safe storage in text columns. The function intentionally raises on
    # unexpected errors so callers can surface signing failures.
    private_key = _load_active_private_key()
    signature = private_key.sign(
        canonical_json_bytes(fields),
        asym_padding.PSS(
            mgf=asym_padding.MGF1(hashes.SHA256()),
            salt_length=asym_padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("ascii")


def verify_signature(fields: dict[str, str | int], signature_b64: str) -> bool:
    # Loads the active public key and verifies the provided
    # base64-encoded signature against the canonical JSON bytes using RSA-
    # PSS. Returns `True` on success and `False` if verification fails or
    # any error occurs.
    try:
        public_key = _load_active_public_key()
        public_key.verify(
            base64.b64decode(signature_b64.encode("ascii"), validate=True),
            canonical_json_bytes(fields),
            asym_padding.PSS(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                salt_length=asym_padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False
