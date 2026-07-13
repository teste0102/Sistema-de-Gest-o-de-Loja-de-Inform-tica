"""
config.py - Configurações de ambiente e banco de dados
Detecta SO e gerencia conexões
"""

import os
import platform
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Settings globais da aplicação"""
    
    # App
    APP_NAME: str = "Sistema Loja Informatica"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DB_TYPE: str = os.getenv("DB_TYPE", "postgresql")  # postgresql ou access
    
    # PostgreSQL
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "loja_informatica")
    
    # Access (backup)
    ACCESS_CADA: Optional[str] = os.getenv("ACCESS_CADA", None)
    ACCESS_OS: Optional[str] = os.getenv("ACCESS_OS", None)
    ACCESS_CAIXA: Optional[str] = os.getenv("ACCESS_CAIXA", None)
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Offline Sync
    ENABLE_OFFLINE_SYNC: bool = True
    SYNC_TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

def get_db_url():
    """Retorna a URL de conexão do banco"""
    if settings.DB_TYPE == "postgresql":
        return f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    return None

def detect_os():
    """Detecta o sistema operacional"""
    system = platform.system()
    return {
        "system": system,
        "release": platform.release(),
        "version": platform.version(),
        "is_windows": system == "Windows",
        "is_linux": system == "Linux",
        "is_macos": system == "Darwin"
    }

def validate_db_connection():
    """Valida conexão com banco de dados"""
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(get_db_url())
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return {"status": "ok", "message": "Conexão BD OK"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
