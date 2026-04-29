from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings:
    app_name: str = "Persistent Memory Tutor"
    database_url: str = os.getenv(
        "MEMORY_TUTOR_DATABASE_URL",
        f"sqlite:///{DATA_DIR / 'memory_tutor.db'}",
    )
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-change-me")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    chroma_dir: Path = DATA_DIR / "chroma"


settings = Settings()

