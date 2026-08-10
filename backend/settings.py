from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    supabase_url: str
    supabase_key: str
    admin_api_key: str
    supabase_password: str

settings = Settings()