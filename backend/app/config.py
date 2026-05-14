from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Sanjeevani"
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "sanjeevani"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 120
    openweather_api_key: str = ""
    openweather_base_url: str = "https://api.openweathermap.org"
    thingspeak_base_url: str = "https://api.thingspeak.com"
    thingspeak_channel_id: str = ""
    thingspeak_read_api_key: str = ""
    ollama_generate_url: str = "http://localhost:11434/api/generate"
    ollama_model: str = "llama3.2"
    frontend_origin: str = "http://localhost:3000"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
