from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _csv_models(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "LegalEase")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    # Current stable Gemini model documented by Google as of Sep 2026.
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    gemini_fallback_models: tuple[str, ...] = _csv_models(
        os.getenv("GEMINI_FALLBACK_MODELS", "gemini-2.5-pro,gemini-2.5-flash")
    )
    demo_mode: bool = _as_bool(os.getenv("DEMO_MODE"), default=False)
    backend_url: str = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").strip().rstrip("/")
    max_document_type: int = int(os.getenv("MAX_DOCUMENT_TYPE", "150"))
    max_parties: int = int(os.getenv("MAX_PARTIES", "2500"))
    max_terms: int = int(os.getenv("MAX_TERMS", "8000"))
    max_dates: int = int(os.getenv("MAX_DATES", "500"))


settings = Settings()
