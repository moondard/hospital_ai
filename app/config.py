from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    crm_base_url: str
    crm_token: str
    ollama_model: str = "qwen3:8b"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()