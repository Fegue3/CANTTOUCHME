from dataclasses import dataclass

import psycopg
from psycopg.rows import dict_row

from app.config import get_settings


@dataclass(frozen=True)
class DatabaseStatus:
    status: str
    detail: str | None = None


def check_database() -> DatabaseStatus:
    settings = get_settings()

    try:
        with psycopg.connect(settings.database_url, connect_timeout=3) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

        if result and result[0] == 1:
            return DatabaseStatus(status="ok")

        return DatabaseStatus(status="error", detail="Unexpected database response")
    except Exception as exc:
        return DatabaseStatus(status="error", detail=str(exc))


def get_connection() -> psycopg.Connection:
    settings = get_settings()
    return psycopg.connect(settings.database_url, row_factory=dict_row)


def init_db() -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY,
                    email VARCHAR UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    encryption_salt TEXT NOT NULL,
                    integrity_salt TEXT NOT NULL,
                    encryption_algorithm VARCHAR NOT NULL
                        CHECK (encryption_algorithm IN ('AES-128-CBC', 'AES-128-CTR')),
                    hmac_algorithm VARCHAR NOT NULL
                        CHECK (hmac_algorithm IN ('HMAC-SHA256', 'HMAC-SHA512')),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    id UUID PRIMARY KEY,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    block_index INTEGER NOT NULL,
                    previous_hash TEXT NOT NULL,
                    iv_or_nonce TEXT NOT NULL,
                    ciphertext TEXT NOT NULL,
                    hmac TEXT NOT NULL,
                    block_hash TEXT NOT NULL,
                    rsa_signature TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(user_id, block_index)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS system_keys (
                    id UUID PRIMARY KEY,
                    public_key TEXT NOT NULL,
                    private_key_encrypted TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    active BOOLEAN NOT NULL DEFAULT TRUE
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chain_state (
                    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    last_hash TEXT NOT NULL,
                    block_count INTEGER NOT NULL,
                    rsa_signature TEXT NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_records_user_block_index
                    ON records(user_id, block_index)
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_records_user_created_at
                    ON records(user_id, created_at)
                """
            )
        connection.commit()
