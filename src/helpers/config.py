from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    # MONGODB_URL:str
    # MONGO_DATABASE:str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str
    
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str 
    OPENAI_API_URL: str 
    COHERE_API_KEY: str 
    GENERATION_MODEL_ID_LITERAL: List[str] 
    GENERATION_MODEL_ID: str 
    EMBEDDING_MODEL_ID: str 
    EMBEDDING_MODEL_SIZE: int 
    INPUT_DAFAULT_MAX_CHARACTERS: int  
    GENERATION_DAFAULT_MAX_TOKENS: int  
    GENERATION_DAFAULT_TEMPERATURE: float  
    VECTOR_DB_BACKEND_LITERAL: List[str]  
    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    VECTOR_DB_DISTANCE_METHOD: str  
    VECTOR_DB_PGVEC_INDEX_THRESHOLD: int = 100

    DEFAULT_LANG:str ="en"
    PRIMARY_LANG:str ="ar"
    # Celery Configuration
    CELERY_BROKER_URL: str  
    CELERY_RESULT_BACKEND: str  
    CELERY_TASK_SERIALIZER: str 
    CELERY_TASK_TIME_LIMIT: int 
    CELERY_TASK_ACKS_LATE: bool
    CELERY_WORKER_CONCURRENCY: int
    CELERY_FLOWER_PASSWORD: str
    

    class Config:
        env_file = ".env"
        

def get_settings():
    return Settings()