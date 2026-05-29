# Authentication dependencies that resolve the active user session.

from dataclasses import dataclass
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import get_connection
from app.services.jwt_service import decode_access_token
from app.services.session_service import SessionKeys, get_session


security = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    # Resolved user, session and session identifier for protected routes.

    user: dict
    session: SessionKeys
    session_id: str


def get_user_by_id(user_id: UUID) -> dict | None:
    # Fetch the public user record needed by authenticated endpoints.
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, email, encryption_algorithm, hmac_algorithm
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )
            return cursor.fetchone()


def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthContext:
    # Validate the bearer token and return the associated auth context.
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
        session_id = payload["sid"]
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from None

    session = get_session(session_id)
    if session is None or session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )

    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )

    return AuthContext(user=user, session=session, session_id=session_id)
