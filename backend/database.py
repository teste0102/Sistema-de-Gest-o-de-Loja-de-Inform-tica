"""
database.py - Gerenciamento de conexão e sessão com banco de dados
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from config import settings, get_db_url

# Criar engine
engine = create_engine(
    get_db_url(),
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Valida conexão antes de usar
    pool_recycle=3600,   # Recicla conexão a cada 1 hora
)

# Factory de sessões
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db() -> Session:
    """Dependency para FastAPI - retorna sessão DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializa o banco - cria todas as tabelas"""
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Banco de dados inicializado!")

def drop_all():
    """CUIDADO: Deleta TUDO do banco"""
    from models import Base
    Base.metadata.drop_all(bind=engine)
    print("⚠️  Banco limpo!")
