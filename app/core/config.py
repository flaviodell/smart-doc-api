from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings and environment variables configuration.
    """
    DATABASE_URL: str
    GROQ_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379/0"

    # Using ConfigDict to avoid Pydantic V2 deprecation warnings
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()