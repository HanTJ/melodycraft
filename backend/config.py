import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# .env 로컬 설정 로드 (없으면 무시)
load_dotenv(BASE_DIR / ".env")


def get_openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY")


def get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_allowed_origins() -> list[str]:
    return ["http://localhost:3000", "http://127.0.0.1:3000"]
