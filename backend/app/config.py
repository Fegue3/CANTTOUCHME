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
    )
