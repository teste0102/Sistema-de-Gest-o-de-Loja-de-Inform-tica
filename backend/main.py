"""
main.py - Aplicação FastAPI principal
Inicia o servidor e gerencia rotas
"""

import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings, detect_os, validate_db_connection
from database import init_db, get_db
from routes import clientes, ordens, financeiro, sync, webhook

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar app FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para Sistema de Gestão de Loja e Ordens de Serviço",
)

# ===== MIDDLEWARE =====

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== STARTUP/SHUTDOWN =====

@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação"""
    logger.info("🚀 Iniciando aplicação...")
    
    # Detectar SO
    os_info = detect_os()
    logger.info(f"SO Detectado: {os_info['system']} {os_info['release']}")
    
    # Validar conexão BD
    db_status = validate_db_connection()
    if db_status["status"] == "ok":
        logger.info("✅ Conexão com BD OK")
        init_db()  # Criar tabelas se não existir
    else:
        logger.warning(f"⚠️  BD Desconectado: {db_status['message']}")
    
    logger.info(f"✅ {settings.APP_NAME} iniciado na versão {settings.APP_VERSION}")

@app.on_event("shutdown")
async def shutdown_event():
    """Executado ao desligar a aplicação"""
    logger.info("🛑 Desligando aplicação...")

# ===== ROTAS HEALTH CHECK =====

@app.get("/", tags=["info"])
async def root():
    """Rota raiz - verifica se API está online"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online"
    }

@app.get("/health", tags=["info"])
async def health():
    """Health check da API"""
    os_info = detect_os()
    db_status = validate_db_connection()
    
    return {
        "status": "healthy" if db_status["status"] == "ok" else "degraded",
        "database": db_status["status"],
        "system": os_info["system"],
        "timestamp": None
    }

# ===== INCLUIR ROTAS DOS MÓDULOS =====

app.include_router(clientes.router, prefix="/api/clientes", tags=["Clientes"])
app.include_router(ordens.router, prefix="/api/ordens", tags=["Ordens"])
app.include_router(financeiro.router, prefix="/api/financeiro", tags=["Financeiro"])
app.include_router(sync.router, prefix="/api/sync", tags=["Sincronização"])
app.include_router(webhook.router, prefix="/api", tags=["Webhooks"])

# ===== TRATAMENTO DE ERROS =====

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Tratamento global de exceções"""
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "Erro interno do servidor", "detail": str(exc)}
    )

# ===== MAIN =====

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
