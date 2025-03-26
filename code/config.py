from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    CONFIG_PATH: str = "config/current_config.json"
    
    class Config:
        env_file = ".env"

settings = Settings()