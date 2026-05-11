from dataclasses import dataclass

import psycopg

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
