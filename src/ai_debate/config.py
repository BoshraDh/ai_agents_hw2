from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str = ""  # unused in CLI mode — kept for .env compatibility
    model: str = "claude-sonnet-4-6"
    max_rounds: int = 10
    min_words: int = 80
    max_words: int = 120
    rate_limit_rpm: int = 30  # higher default for local CLI mode

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
