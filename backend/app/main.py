from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import check_database, init_db
from app.routes import auth, records
from app.services.rsa_service import ensure_active_system_key


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    ensure_active_system_key()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "CANTTOUCHME API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    database = check_database()
    return {
        "api": "ok",
        "database": database.status,
    }


app.include_router(auth.router)
app.include_router(records.router)
