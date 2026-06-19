from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str 
    APP_VERSION: str 
    LLAMA_PARSER_API_KEY: str 
    
    FILE_ALLOWED_TYPES: list 
    FILE_MAX_SIZE: int = 20
    FILE_CHUNCK_SIZE: int = 1000
    
    MONGODB_URL: str 
    MONGODB_NAME: str 
    
    GENERATION_BACKEND : str 
    EMBEDING_BACKEND : str 

    OPENAI_KEY : str
    OPENAI_URL  : str

    GENERATION_MODEL_ID : str 
    EMBEDING_MODEL_ID: str 

    INPUT_DEFAULT_MAX_CHARARACTERS : int
    GENERATION_DEFAULT_MAX_TOKENS : int
    GENERATION_DEFAULT_TEMPERATURE : float
    EMBEDING_MODEL_SIZE: int
    
    VECTOR_DB_BACKEND : str 
    VECTOR_DB_PATH : str 
    VECTOR_DB_DIStANCE : str 
 
    model_config = SettingsConfigDict(env_file=".env")

def get_settings():
    return Settings() # type: ignore