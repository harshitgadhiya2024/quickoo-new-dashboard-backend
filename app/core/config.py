from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = Field(default="Quickoo Backend", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")

    mongodb_uri: str = Field(alias="MONGODB_URI")
    mongodb_db_name: str = Field(default="quickoo", alias="MONGODB_DB_NAME")

    smtp_host: str = Field(alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_secure: bool = Field(default=False, alias="SMTP_SECURE")
    smtp_user: str = Field(alias="SMTP_USER")
    smtp_pass: str = Field(alias="SMTP_PASS")
    smtp_from: str = Field(alias="SMTP_FROM")
    booking_admin_email: str = Field(alias="BOOKING_ADMIN_EMAIL")

    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    aws_access_key_id: str = Field(alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(alias="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(alias="AWS_REGION")
    s3_bucket_name: str = Field(alias="S3_BUCKET_NAME")

    stripe_secret_key: str = Field(alias="STRIPE_SECRET_KEY")
    stripe_api_version: Optional[str] = Field(default=None, alias="STRIPE_API_VERSION")

    @field_validator("stripe_api_version", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: Optional[str]) -> Optional[str]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        return v

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
