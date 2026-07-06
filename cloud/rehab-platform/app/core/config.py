from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Lingdong Rehab Cloud"
    database_url: str = "sqlite+pysqlite:///./rehab-platform.db"
    jwt_secret: str = "dev-rehab-platform-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 60 * 24 * 7

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
