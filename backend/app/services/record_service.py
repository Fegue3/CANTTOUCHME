from __future__ import annotations

import json
from datetime import date, datetime, time, timezone
from typing import Any
from uuid import UUID, uuid4

from app.database import get_connection
from app.schemas.record import RecordItem, RecordValidation
from app.services import crypto_service, rsa_service
from app.services.crypto_service import EncryptionAlgorithm, HmacAlgorithm
from app.services.session_service import SessionKeys
from app.utils.canonical_json import canonical_json_bytes


GENESIS_HASH = "GENESIS"


def _record_payload(text: str, timestamp: datetime) -> dict[str, str]:
    return {
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "text": text,
    }


def _protected_fields(
    user_id: str,
    block_index: int,
    previous_hash: str,
    iv_or_nonce: str,
    ciphertext: str,
    encryption_algorithm: str,
    hmac_algorithm: str,
) -> dict[str, str | int]:
    return {
        "user_id": user_id,
        "block_index": block_index,
        "previous_hash": previous_hash,
        "iv_or_nonce": iv_or_nonce,
        "ciphertext": ciphertext,
        "encryption_algorithm": encryption_algorithm,
        "hmac_algorithm": hmac_algorithm,
    }


def create_record(user: dict[str, Any], session: SessionKeys, text: str) -> dict[str, Any]:
    record_id = uuid4()
    timestamp = datetime.now(timezone.utc)
    encryption_algorithm = user["encryption_algorithm"]
    hmac_algorithm = user["hmac_algorithm"]
    payload = canonical_json_bytes(_record_payload(text, timestamp))
    iv_or_nonce, ciphertext = crypto_service.encrypt_payload(
        payload,
        session.encryption_key,
        encryption_algorithm,
    )

    with get_connection() as connection:
        with connection.transaction():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM users WHERE id = %s FOR UPDATE",
                    (user["id"],),
                )
                cursor.execute(
                    """
                    SELECT block_index, block_hash
                    FROM records
                    WHERE user_id = %s
                    ORDER BY block_index DESC
                    LIMIT 1
                    FOR UPDATE
                    """,
                    (user["id"],),
                )
                previous = cursor.fetchone()
                block_index = 1 if previous is None else previous["block_index"] + 1
                previous_hash = GENESIS_HASH if previous is None else previous["block_hash"]
                protected = _protected_fields(
                    str(user["id"]),
                    block_index,
                    previous_hash,
                    iv_or_nonce,
                    ciphertext,
                    encryption_algorithm,
                    hmac_algorithm,
                )
                hmac_value = crypto_service.compute_hmac(
                    session.integrity_key,
                    hmac_algorithm,
                    protected,
                )
                block_hash = crypto_service.compute_block_hash({**protected, "hmac": hmac_value})
                signature = rsa_service.sign_block(
                    rsa_service.signature_fields(
                        str(user["id"]),
                        block_index,
                        previous_hash,
                        block_hash,
                    )
                )
                cursor.execute(
                    """
                    INSERT INTO records (
                        id, user_id, block_index, previous_hash, iv_or_nonce,
                        ciphertext, hmac, block_hash, rsa_signature, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        record_id,
                        user["id"],
                        block_index,
                        previous_hash,
                        iv_or_nonce,
                        ciphertext,
                        hmac_value,
                        block_hash,
                        signature,
                        timestamp,
                    ),
                )

    return {"id": str(record_id), "block_index": block_index}


def fetch_user_records(user_id: UUID) -> list[dict[str, Any]]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, block_index, previous_hash, iv_or_nonce, ciphertext,
                       hmac, block_hash, rsa_signature, created_at
                FROM records
                WHERE user_id = %s
                ORDER BY block_index ASC
                """,
                (user_id,),
            )
            return list(cursor.fetchall())


def _overall_status(
    hmac_valid: bool,
    block_hash_valid: bool,
    previous_valid: bool,
    rsa_valid: bool,
    decrypt_valid: bool,
    chain_was_broken: bool,
) -> str:
    if not previous_valid:
        return "invalid_previous_hash"
    if not hmac_valid:
        return "invalid_hmac"
    if not block_hash_valid:
        return "invalid_block_hash"
    if not rsa_valid:
        return "invalid_rsa_signature"
    if not decrypt_valid:
        return "decrypt_error"
    if chain_was_broken:
        return "chain_affected"
    return "valid"


def validate_records(user: dict[str, Any], session: SessionKeys) -> list[RecordItem]:
    rows = fetch_user_records(user["id"])
    encryption_algorithm: EncryptionAlgorithm = user["encryption_algorithm"]
    hmac_algorithm: HmacAlgorithm = user["hmac_algorithm"]
    previous_stored_hash = GENESIS_HASH
    previous_index = 0
    chain_broken = False
    items: list[RecordItem] = []

    for row in rows:
        protected = _protected_fields(
            str(row["user_id"]),
            row["block_index"],
            row["previous_hash"],
            row["iv_or_nonce"],
            row["ciphertext"],
            encryption_algorithm,
            hmac_algorithm,
        )
        expected_previous = previous_stored_hash
        expected_index = previous_index + 1
        previous_valid = (
            row["previous_hash"] == expected_previous
            and row["block_index"] == expected_index
        )
        hmac_valid = crypto_service.verify_hmac(
            session.integrity_key,
            hmac_algorithm,
            protected,
            row["hmac"],
        )
        expected_block_hash = crypto_service.compute_block_hash({**protected, "hmac": row["hmac"]})
        block_hash_valid = expected_block_hash == row["block_hash"]
        rsa_valid = rsa_service.verify_signature(
            rsa_service.signature_fields(
                str(row["user_id"]),
                row["block_index"],
                row["previous_hash"],
                row["block_hash"],
            ),
            row["rsa_signature"],
        )

        timestamp: str | None = None
        text: str | None = None
        decrypt_valid = False
        decrypt_status = "not_checked"
        if hmac_valid:
            try:
                plaintext = crypto_service.decrypt_payload(
                    row["ciphertext"],
                    row["iv_or_nonce"],
                    session.encryption_key,
                    encryption_algorithm,
                )
                payload = json.loads(plaintext.decode("utf-8"))
                timestamp = payload.get("timestamp")
                text = payload.get("text")
                decrypt_valid = isinstance(timestamp, str) and isinstance(text, str)
                decrypt_status = "valid" if decrypt_valid else "decrypt_error"
            except Exception:
                decrypt_status = "decrypt_error"

        overall = _overall_status(
            hmac_valid,
            block_hash_valid,
            previous_valid,
            rsa_valid,
            decrypt_valid,
            chain_broken,
        )
        validation = RecordValidation(
            hmac="valid" if hmac_valid else "invalid",
            block_hash="valid" if block_hash_valid else "invalid",
            previous_hash="valid" if previous_valid else "invalid",
            rsa_signature="valid" if rsa_valid else "invalid",
            decrypt=decrypt_status,
            overall=overall,
        )
        items.append(
            RecordItem(
                id=str(row["id"]),
                block_index=row["block_index"],
                timestamp=timestamp,
                text=text,
                created_at=row["created_at"],
                validation=validation,
            )
        )

        if overall != "valid":
            chain_broken = True
        previous_stored_hash = row["block_hash"]
        previous_index = row["block_index"]

    return items


def filter_records(
    records: list[RecordItem],
    start_date: date | None,
    end_date: date | None,
    status: str | None,
) -> list[RecordItem]:
    filtered = records
    if start_date is not None:
        start_at = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        filtered = [record for record in filtered if record.created_at >= start_at]
    if end_date is not None:
        end_at = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        filtered = [record for record in filtered if record.created_at <= end_at]
    if status == "valid":
        filtered = [record for record in filtered if record.validation.overall == "valid"]
    elif status == "invalid":
        filtered = [record for record in filtered if record.validation.overall != "valid"]
    return filtered


def find_record_for_user(record_id: UUID, user_id: UUID) -> dict[str, Any] | None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM records
                WHERE id = %s AND user_id = %s
                """,
                (record_id, user_id),
            )
            return cursor.fetchone()
