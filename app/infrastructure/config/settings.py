from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _cors_to_list(s: str) -> List[str]:
    if s.strip() in ("", "*"):
        return ["*"]
    return [x.strip() for x in s.split(",") if x.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env",), env_file_encoding="utf-8", extra="ignore"
    )
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    # Local/teste: sqlite em memória. Docker/Produção: defina postgresql+psycopg2://...
    database_url: str = Field(
        default="sqlite:///:memory:",
        validation_alias="DATABASE_URL",
    )
    jwt_secret: str = Field(
        default="chave-dev-alterar-em-producao-min-8-chars",
        validation_alias="JWT_SECRET",
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(60, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    cors_origins: str = Field(default="*", validation_alias="CORS_ORIGINS")
    webhook_api_key: str = Field(
        default="chave-webhook-dev-alterar",
        validation_alias="WEBHOOK_API_KEY",
    )
    email_enabled: bool = Field(default=False, validation_alias="EMAIL_ENABLED")
    smtp_host: str = Field(default="localhost", validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    smtp_user: str = Field(default="", validation_alias="SMTP_USER")
    smtp_password: str = Field(default="", validation_alias="SMTP_PASSWORD")
    email_from: str = Field(default="oficina@localhost", validation_alias="EMAIL_FROM")

    @field_validator("email_enabled", mode="before")
    @classmethod
    def v_email_enabled(cls, v: str | bool) -> bool:
        if isinstance(v, bool):
            return v
        return str(v).strip().lower() in ("1", "true", "yes", "on")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def v_cors(cls, v: str | list) -> str:
        if isinstance(v, list):
            return ",".join(v)
        return v or "*"

    def get_cors_origins_list(self) -> List[str]:
        return _cors_to_list(self.cors_origins)

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
