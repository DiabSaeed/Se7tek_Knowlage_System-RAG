from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_KEY: str
    LLAMA_PARSER_API_KEY: str
    
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_CHUNCK_SIZE: int
    
    MONGODB_URL: str
    MONGODB_NAME: str
    
    # التعديل هنا: شلنا class Config واستخدمنا model_config
    model_config = SettingsConfigDict(env_file=".env")

def get_settings():
    return Settings() # ignore