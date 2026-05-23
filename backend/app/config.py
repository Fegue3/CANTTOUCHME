from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str
    database_url: str
    backend_cors_origins: list[str]
    jwt_secret_key: str
    access_token_expire_minutes: int
    session_expire_minutes: int
    bcrypt_cost: int
    pbkdf2_iterations: int
    system_rsa_key_encryption_secret: str


@lru_cache
def get_settings() -> Settings:
    load_dotenv()

    return Settings(
        app_name=os.getenv("APP_NAME", "CANTTOUCHME API"),
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql://canttouchme:canttouchme@localhost:5432/canttouchme",
        ),
        backend_cors_origins=_split_csv(
            os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5173")
        ),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", "dev-only-change-this-jwt-secret-32-bytes-min"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        session_expire_minutes=int(os.getenv("SESSION_EXPIRE_MINUTES", "30")),
        bcrypt_cost=int(os.getenv("BCRYPT_COST", "12")),
        pbkdf2_iterations=int(os.getenv("PBKDF2_ITERATIONS", "600000")),
        system_rsa_key_encryption_secret=os.getenv(
            "SYSTEM_RSA_KEY_ENCRYPTION_SECRET",
            "dev-only-change-this-rsa-secret",
        ),
    )
