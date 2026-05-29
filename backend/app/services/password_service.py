# Password hashing helpers built on bcrypt.

import bcrypt

from app.config import get_settings


def hash_password(password: str) -> str:
    # Hash a plaintext password with the configured bcrypt cost.
    settings = get_settings()
    salt = bcrypt.gensalt(rounds=settings.bcrypt_cost)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    # Check whether a plaintext password matches a stored bcrypt hash.
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False
