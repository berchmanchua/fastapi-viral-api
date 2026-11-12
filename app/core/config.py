from typing import Annotated, Literal
from pydantic import AfterValidator, Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

PostgresDsnStr = Annotated[PostgresDsn, AfterValidator(str)]
RedisDsnStr = Annotated[RedisDsn, AfterValidator(str)]


class Settings(BaseSettings):
    PROJECT_NAME: str = "ViralAPI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    DATABASE_URL: PostgresDsnStr
    VALKEY_URL: RedisDsnStr

    DB_POOL_MIN_SIZE: int = Field(default=5, ge=1, le=50)
    DB_POOL_MAX_SIZE: int = Field(default=20, ge=5, le=200)
    CACHE_TTL_SECONDS: int = Field(default=3600, ge=60)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
