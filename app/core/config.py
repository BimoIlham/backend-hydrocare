from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Konfigurasi aplikasi dari file .env"""
    openweather_api_key: str
    database_url: str = "sqlite:///./hydrocare.db"
    secret_key: str = "hydrocare-dev-secret"
    city_default: str = "Bandar Lampung"
    allowed_origins: str = "https://frontend-hydrocare.vercel.app"
    
    # Supabase config (optional)
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    
    # AI Config
    gemini_api_key: Optional[str] = None

    class Config:
        env_file = ".env"

# Instance tunggal (singleton pattern)
settings = Settings()