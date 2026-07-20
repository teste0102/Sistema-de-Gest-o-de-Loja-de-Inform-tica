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
import asyncio
from routes import clientes, ordens, financeiro, sync, webhook, numeros_os, senhas, fotos, laudo, auth, mdb_sync, produtos, vendas, sync_auto

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

def _ciclo_sync_automatica() -> int:
    """Executa um ciclo de sincronização entre terminais (roda numa thread).
    Retorna o intervalo em minutos para o próximo ciclo."""
    from database import SessionLocal
    from routes.sync_auto import obter_config
    from services import sync_terminais
    from datetime import datetime as _dt

    db = SessionLocal()
    try:
        cfg = obter_config(db)
        intervalo = int(cfg.intervalo_min or 5)
        if not cfg.ativo:
            return intervalo
        total = sync_terminais.sincronizar(db, cfg)
        cfg.ultima_sync = _dt.utcnow()
        cfg.ultimo_status = (
            f"AUTO OK: clientes {total['clientes']}, produtos {total['produtos']}, "
            f"vendas {total['vendas']}, estoque {total.get('movimentos', 0)} "
            f"({total['terminais']} terminal/is)"
        )
        db.add(cfg)
        db.commit()
        logger.info(f"🔄 {cfg.ultimo_status}")
        return int(cfg.intervalo_min or 5)
    finally:
        db.close()


async def _loop_sync_automatica():
    """Laço da sincronização automática. Respeita o intervalo configurado."""
    # Pequena espera inicial para o app subir por completo
    await asyncio.sleep(20)
    while True:
        intervalo = 5
        try:
            intervalo = await asyncio.get_event_loop().run_in_executor(None, _ciclo_sync_automatica)
        except Exception as e:
            logger.warning(f"⚠️  Sync automática falhou (ignorado): {e}")
        await asyncio.sleep(max(1, int(intervalo)) * 60)


@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação"""
    logger.info("🚀 Iniciando aplicação...")

    # Inicia a sincronização automática entre terminais em segundo plano
    try:
        asyncio.create_task(_loop_sync_automatica())
        logger.info("🔄 Sincronização automática agendada")
    except Exception as e:
        logger.warning(f"⚠️  Não foi possível iniciar a sync automática: {e}")
    
    # Detectar SO
    os_info = detect_os()
    logger.info(f"SO Detectado: {os_info['system']} {os_info['release']}")
    
    # Validar conexão BD
    db_status = validate_db_connection()
    if db_status["status"] == "ok":
        logger.info("✅ Conexão com BD OK")
        init_db()  # Criar tabelas se não existir
        # Popular dados iniciais (cliente/OS/lançamento de exemplo)
        try:
            from seed import seed_dados_iniciais
            seed_dados_iniciais()
        except Exception as e:
            logger.warning(f"⚠️  Falha no seed inicial (ignorado): {e}")
        # Gera a contagem base do estoque para produtos ainda sem movimento
        try:
            from database import SessionLocal
            from services.estoque_service import backfill_baselines
            _db = SessionLocal()
            try:
                n = backfill_baselines(_db)
                if n:
                    logger.info(f"📦 Contagem base criada para {n} produto(s)")
            finally:
                _db.close()
        except Exception as e:
            logger.warning(f"⚠️  Falha no backfill de estoque (ignorado): {e}")
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
app.include_router(numeros_os.router, prefix="/api/os", tags=["Números OS"])
app.include_router(senhas.router, prefix="/api/os", tags=["Senhas"])
app.include_router(fotos.router, prefix="/api/os", tags=["Fotos"])
app.include_router(laudo.router, prefix="/api/os", tags=["Laudos Técnicos"])
app.include_router(produtos.router, prefix="/api/produtos", tags=["Produtos / Estoque"])
app.include_router(vendas.router, prefix="/api/vendas", tags=["Vendas"])
app.include_router(sync_auto.router, prefix="/api/sync-auto", tags=["Sincronização Automática"])
app.include_router(financeiro.router, prefix="/api/financeiro", tags=["Financeiro"])
app.include_router(sync.router, prefix="/api/sync", tags=["Sincronização"])
app.include_router(mdb_sync.router, prefix="/api/sync", tags=["Sincronização MDB"])
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
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
