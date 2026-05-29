# JWT helpers for issuing and decoding short-lived access tokens.

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from app.config import get_settings


JWT_ALGORITHM = "HS256"


def create_access_token(user_id: UUID, session_id: str) -> tuple[str, int]:
    # Create a bearer token tied to a user and the current session.
    settings = get_settings()
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expires_at = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(user_id),
        "sid": session_id,
        "exp": expires_at,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)
    return token, int(expires_delta.total_seconds())


def decode_access_token(token: str) -> dict[str, str]:
    # Decode a bearer token and verify its signature and expiry.
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[JWT_ALGORITHM])
