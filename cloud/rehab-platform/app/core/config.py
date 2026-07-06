from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Lingdong Rehab Cloud"
    database_url: str = "sqlite+pysqlite:///./rehab-platform.db"
    jwt_secret: str = "dev-rehab-platform-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 60 * 24 * 7
    phone_verification_debug_code_enabled: bool = True
    phone_verification_ttl_seconds: int = 300
    phone_verification_max_attempts: int = 5
    agent_model_provider: str = "openai_compatible"
    agent_model_base_url: str = "https://api.openai.com/v1"
    agent_model_api_key: str | None = None
    agent_model_name: str = "gpt-4o-mini"
    agent_model_timeout_seconds: float = 8.0
    agent_model_temperature: float = 0.2
    agent_model_max_tokens: int = 500

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
