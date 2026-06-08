from __future__ import annotations

import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_RATE_LIMITS_FILE = Path(__file__).parent.parent.parent / "config" / "rate_limits.json"


def _load_default_rpm() -> int:
    try:
        data = json.loads(_RATE_LIMITS_FILE.read_text(encoding="utf-8"))
        return int(data["rate_limits"]["services"]["default"]["requests_per_minute"])
    except Exception:
        return 30


class Settings(BaseSettings):
    anthropic_api_key: str = ""  # unused in CLI mode — kept for .env compatibility
    model: str = "claude-sonnet-4-6"
    max_rounds: int = 10
    min_words: int = 80
    max_words: int = 120
    rate_limit_rpm: int = _load_default_rpm()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()  # type: ignore[call-arg]
