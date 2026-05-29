# In-memory session storage for access-token backed authentication.

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import secrets
from threading import Lock
from uuid import UUID

from app.config import get_settings


@dataclass(frozen=True)
class SessionKeys:
    # Session metadata plus the derived keys kept in memory.

    session_id: str
    user_id: UUID
    encryption_key: bytes
    integrity_key: bytes
    expires_at: datetime


_sessions: dict[str, SessionKeys] = {}
_lock = Lock()


def create_session(user_id: UUID, encryption_key: bytes, integrity_key: bytes) -> SessionKeys:
    # Generates a cryptographically strong random session id and an
    # expiry timestamp. Stores the `SessionKeys` dataclass in the in-memory
    # `_sessions` dict while holding a lock and runs a short cleanup of expired
    # sessions. NOTE: this in-memory approach is convenient for development
    # and tests but will not scale across multiple processes or survive restarts.
    settings = get_settings()
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.session_expire_minutes)
    session = SessionKeys(
        session_id=session_id,
        user_id=user_id,
        encryption_key=encryption_key,
        integrity_key=integrity_key,
        expires_at=expires_at,
    )

    with _lock:
        cleanup_expired_sessions()
        _sessions[session_id] = session

    return session


def get_session(session_id: str) -> SessionKeys | None:
    # Atomically checks the session dictionary under a lock and
    # removes the entry if the expiry time has passed. Callers should treat
    # the returned `SessionKeys` as short-lived and avoid persisting derived
    # keys elsewhere. For production, replace with a shared session store
    # (Redis, database-backed tokens, or similar).
    with _lock:
        session = _sessions.get(session_id)
        if session is None:
            return None
        if session.expires_at <= datetime.now(timezone.utc):
            _sessions.pop(session_id, None)
            return None
        return session


def delete_session(session_id: str) -> None:
    # Remove a session immediately.
    with _lock:
        _sessions.pop(session_id, None)


def cleanup_expired_sessions() -> None:
    # Drop any sessions that have reached their expiry time.
    now = datetime.now(timezone.utc)
    expired = [
        session_id
        for session_id, session in _sessions.items()
        if session.expires_at <= now
    ]
    for session_id in expired:
        _sessions.pop(session_id, None)


def clear_sessions() -> None:
    # Remove every in-memory session, usually for tests or shutdown.
    with _lock:
        _sessions.clear()
