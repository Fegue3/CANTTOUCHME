from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_connection
from app.dependencies import AuthContext, require_auth
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RegisterRequest,
    UserPublic,
)
from app.services import crypto_service, password_service
from app.services.jwt_service import create_access_token
from app.services.session_service import create_session, delete_session


router = APIRouter(prefix="/auth", tags=["auth"])


def _get_user_by_email(email: str) -> dict | None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, email, password_hash, encryption_salt, integrity_salt,
                       encryption_algorithm, hmac_algorithm
                FROM users
                WHERE email = %s
                """,
                (email.lower(),),
            )
            return cursor.fetchone()


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> MessageResponse:
    email = payload.email.lower()
    if _get_user_by_email(email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    encryption_salt = crypto_service.random_b64(16)
    integrity_salt = crypto_service.random_b64(16)
    password_hash = password_service.hash_password(payload.password)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (
                    id, email, password_hash, encryption_salt, integrity_salt,
                    encryption_algorithm, hmac_algorithm
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    uuid4(),
                    email,
                    password_hash,
                    encryption_salt,
                    integrity_salt,
                    payload.encryption_algorithm,
                    payload.hmac_algorithm,
                ),
            )
        connection.commit()

    return MessageResponse(message="User registered successfully")


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    user = _get_user_by_email(payload.email)
    if user is None or not password_service.verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    encryption_key, integrity_key = crypto_service.derive_user_keys(
        payload.password,
        user["encryption_salt"],
        user["integrity_salt"],
    )
    session = create_session(user["id"], encryption_key, integrity_key)
    token, expires_in = create_access_token(user["id"], session.session_id)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserPublic(
            email=user["email"],
            encryption_algorithm=user["encryption_algorithm"],
            hmac_algorithm=user["hmac_algorithm"],
        ),
    )


@router.post("/logout", response_model=MessageResponse)
def logout(context: AuthContext = Depends(require_auth)) -> MessageResponse:
    delete_session(context.session_id)
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserPublic)
def me(context: AuthContext = Depends(require_auth)) -> UserPublic:
    return UserPublic(
        email=context.user["email"],
        encryption_algorithm=context.user["encryption_algorithm"],
        hmac_algorithm=context.user["hmac_algorithm"],
    )
