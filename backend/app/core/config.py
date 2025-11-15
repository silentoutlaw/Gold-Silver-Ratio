"""
Application configuration management using Pydantic Settings.
Loads configuration from environment variables with validation.
"""

from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="allow"
    )

    # Application
    app_name: str = Field(default="GSR Analytics", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # API Server
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_workers: int = Field(default=4, alias="API_WORKERS")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://gsr_user:gsr_password@localhost:5432/gsr_analytics",
        alias="DATABASE_URL",
    )
    database_pool_size: int = Field(default=20, alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=0, alias="DATABASE_MAX_OVERFLOW")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"], alias="CORS_ORIGINS"
    )

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            import json

            return json.loads(v)
        return v

    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production-minimum-32-chars",
        alias="SECRET_KEY",
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # Data Providers - Metals & Markets
    alpha_vantage_api_key: Optional[str] = Field(default=None, alias="ALPHA_VANTAGE_API_KEY")
    metals_api_key: Optional[str] = Field(default=None, alias="METALS_API_KEY")

    # Data Providers - Macro
    fred_api_key: Optional[str] = Field(default=None, alias="FRED_API_KEY")

    # AI Providers
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")

    # AI Configuration
    default_ai_provider: str = Field(default="openai", alias="DEFAULT_AI_PROVIDER")
    default_ai_model_openai: str = Field(
        default="gpt-4-turbo-preview", alias="DEFAULT_AI_MODEL_OPENAI"
    )
    default_ai_model_anthropic: str = Field(
        default="claude-3-sonnet-20240229", alias="DEFAULT_AI_MODEL_ANTHROPIC"
    )
    default_ai_model_google: str = Field(
        default="gemini-pro", alias="DEFAULT_AI_MODEL_GOOGLE"
    )
    ai_max_tokens: int = Field(default=4000, alias="AI_MAX_TOKENS")
    ai_temperature: float = Field(default=0.7, alias="AI_TEMPERATURE")
    ai_timeout_seconds: int = Field(default=60, alias="AI_TIMEOUT_SECONDS")

    # Data Ingestion
    ingestion_schedule_enabled: bool = Field(
        default=True, alias="INGESTION_SCHEDULE_ENABLED"
    )
    ingestion_daily_hour: int = Field(default=20, alias="INGESTION_DAILY_HOUR")
    ingestion_daily_minute: int = Field(default=0, alias="INGESTION_DAILY_MINUTE")
    ingestion_timezone: str = Field(default="UTC", alias="INGESTION_TIMEZONE")

    # Alerts
    alert_email_enabled: bool = Field(default=False, alias="ALERT_EMAIL_ENABLED")
    alert_email_smtp_host: str = Field(default="smtp.gmail.com", alias="ALERT_EMAIL_SMTP_HOST")
    alert_email_smtp_port: int = Field(default=587, alias="ALERT_EMAIL_SMTP_PORT")
    alert_email_from: str = Field(
        default="alerts@gsranalytics.com", alias="ALERT_EMAIL_FROM"
    )
    alert_email_password: Optional[str] = Field(default=None, alias="ALERT_EMAIL_PASSWORD")
    alert_webhook_enabled: bool = Field(default=False, alias="ALERT_WEBHOOK_ENABLED")
    alert_webhook_url: Optional[str] = Field(default=None, alias="ALERT_WEBHOOK_URL")

    # Monitoring
    prometheus_enabled: bool = Field(default=True, alias="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, alias="PROMETHEUS_PORT")

    # Feature Flags
    enable_intraday_data: bool = Field(default=False, alias="ENABLE_INTRADAY_DATA")
    enable_advanced_backtesting: bool = Field(
        default=True, alias="ENABLE_ADVANCED_BACKTESTING"
    )
    enable_ml_regimes: bool = Field(default=False, alias="ENABLE_ML_REGIMES")

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic migrations."""
        return self.database_url.replace("+asyncpg", "").replace(
            "postgresql+asyncpg", "postgresql"
        )


# Global settings instance
settings = Settings()
