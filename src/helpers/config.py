from pydantic_settings import BaseSettings, SettingsConfigDict
# from typing import List
# from pydantic import field_validator

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    # OPENAI_API_KEY: str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    class Config:
        env_file = "src/.env"
    # @field_validator("FILE_ALLOWED_TYPES")
    # def parse_file_allowed_types(cls, value):
    #     if isinstance(value, str):
    #         return [item.strip() for item in value.split(",")]
    #     return value

def get_settings():
    return Settings()
