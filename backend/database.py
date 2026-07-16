"""
database.py - Gerenciamento de conexão e sessão com banco de dados
"""

from sqlalchemy import create_engine, event, text
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

def run_auto_migrations():
    """
    Aplica migrations idempotentes (ADD COLUMN IF NOT EXISTS).
    Necessário porque create_all() não altera tabelas já existentes.
    Seguro: não remove nem sobrescreve dados.
    """
    alteracoes = [
        # Assistente de cadastro de OS (Wizard) - migration 003
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS produto_tipo VARCHAR(30)",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS produto_descricao VARCHAR(255)",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS endereco_rua VARCHAR(150)",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS endereco_tipo VARCHAR(20)",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS endereco_complemento VARCHAR(120)",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS endereco_numero VARCHAR(20)",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS bairro VARCHAR(80)",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS cidade_os VARCHAR(80)",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS telefone_contato VARCHAR(20)",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS problema_descricao TEXT",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS assinatura_cliente TEXT",
        # Orçamento (migration 004)
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS valor_aprovado_estimado DOUBLE PRECISION DEFAULT 0.0",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS valor_aprovado_parcelas INTEGER DEFAULT 1",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS valor_total_estimado DOUBLE PRECISION DEFAULT 0.0",
        "ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS valor_total_parcelas INTEGER DEFAULT 1",
    ]
    with engine.begin() as conn:
        for sql in alteracoes:
            try:
                conn.execute(text(sql))
            except Exception as e:
                print(f"⚠️  Auto-migration ignorada ({sql[:60]}...): {e}")
    print("✅ Auto-migrations aplicadas!")


def init_db():
    """Inicializa o banco - cria todas as tabelas"""
    from models import Base
    Base.metadata.create_all(bind=engine)
    run_auto_migrations()
    print("✅ Banco de dados inicializado!")

def drop_all():
    """CUIDADO: Deleta TUDO do banco"""
    from models import Base
    Base.metadata.drop_all(bind=engine)
    print("⚠️  Banco limpo!")
