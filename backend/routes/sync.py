"""
Rotas para Sincronização Multi-Servidor
Push/Pull com resolução de conflitos e fallback offline
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime

from ..database import get_db
from ..services.sync_service import SyncService, EstrategiaResolucao
from ..utils.crypto_service import CryptoService


router = APIRouter(
    prefix="/api/sync",
    tags=["Sincronização"]
)


# ============================================================================
# SCHEMAS
# ============================================================================

class SyncOperacaoRequest(BaseModel):
    """Schema para enfileirar operação"""
    tabela: str
    operacao: str  # insert, update, delete
    registro_id: int
    dados: Dict


class ServidorRemotoRequest(BaseModel):
    """Schema para registrar servidor remoto"""
    nome: str
    url: str
    chave_api: str
    ativo: bool = True


# ============================================================================
# ENFILEIRAR OPERAÇÃO
# ============================================================================

@router.post("/enfileirar", response_model=Dict)
def enfileirar_operacao(
    request: SyncOperacaoRequest,
    db: Session = Depends(get_db)
):
    """Enfileira operação para sincronização (offline-first)"""
    try:
        crypto = CryptoService()
        sync_svc = SyncService(crypto)

        resultado = sync_svc.enfileirar_operacao(
            db=db,
            tabela=request.tabela,
            operacao=request.operacao,
            registro_id=request.registro_id,
            dados=request.dados
        )

        return resultado

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao enfileirar operação: {str(e)}"
        )


# ============================================================================
# OBTER FILA DE SINCRONIZAÇÃO
# ============================================================================

@router.get("/fila", response_model=Dict)
def obter_fila_sync(
    sincronizado: Optional[bool] = False,
    limite: int = 100,
    db: Session = Depends(get_db)
):
    """Obtém itens da fila de sincronização"""
    try:
        crypto = CryptoService()
        sync_svc = SyncService(crypto)

        itens = sync_svc.obter_fila_sync(db, sincronizado, limite)

        total = len(itens)
        pendentes = sum(1 for i in itens if not i.get("sincronizado"))

        return {
            "ok": True,
            "total": total,
            "pendentes": pendentes,
            "itens": itens
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao obter fila: {str(e)}"
        )


# ============================================================================
# OBTER STATUS DE SINCRONIZAÇÃO
# ============================================================================

@router.get("/status", response_model=Dict)
def obter_status_sync(db: Session = Depends(get_db)):
    """Obtém status geral de sincronização"""
    try:
        crypto = CryptoService()
        sync_svc = SyncService(crypto)

        status_info = sync_svc.obter_status_sync(db)

        return {
            "ok": True,
            "status": status_info
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao obter status: {str(e)}"
        )


# ============================================================================
# REGISTRAR SERVIDOR REMOTO
# ============================================================================

@router.post("/servidores", response_model=Dict)
def registrar_servidor_remoto(
    request: ServidorRemotoRequest,
    db: Session = Depends(get_db)
):
    """Registra novo servidor remoto para sincronização"""
    try:
        crypto = CryptoService()
        sync_svc = SyncService(crypto)

        resultado = sync_svc.registrar_servidor_remoto(
            db=db,
            nome=request.nome,
            url=request.url,
            chave_api=request.chave_api,
            ativo=request.ativo
        )

        return resultado

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao registrar servidor: {str(e)}"
        )


# ============================================================================
# DETECTAR CONFLITO
# ============================================================================

@router.post("/detectar-conflito", response_model=Dict)
def detectar_conflito(
    dados_local: Dict,
    dados_remoto: Dict
):
    """Detecta conflito entre versões local e remota"""
    try:
        crypto = CryptoService()
        sync_svc = SyncService(crypto)

        tem_conflito, tipo = sync_svc.detectar_conflito(dados_local, dados_remoto)

        return {
            "ok": True,
            "tem_conflito": tem_conflito,
            "tipo_conflito": tipo
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao detectar conflito: {str(e)}"
        )


# ============================================================================
# RESOLVER CONFLITO
# ============================================================================

@router.post("/resolver-conflito", response_model=Dict)
def resolver_conflito(
    dados_local: Dict,
    dados_remoto: Dict,
    estrategia: str = "merge_timestamps"
):
    """Resolve conflito entre versões"""
    try:
        crypto = CryptoService()
        sync_svc = SyncService(crypto)

        estrategia_enum = EstrategiaResolucao(estrategia)

        resultado = sync_svc.resolver_conflito(
            dados_local, dados_remoto, estrategia_enum
        )

        return {
            "ok": True,
            "estrategia": estrategia,
            "resultado": resultado
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao resolver conflito: {str(e)}"
        )


# ============================================================================
# GERAR HASH DE DADOS
# ============================================================================

@router.post("/hash", response_model=Dict)
def gerar_hash_dados(dados: Dict):
    """Gera hash SHA-256 de dados para detecção de mudanças"""
    try:
        crypto = CryptoService()
        sync_svc = SyncService(crypto)

        hash_valor = sync_svc.gerar_hash_dados(dados)

        return {
            "ok": True,
            "hash": hash_valor
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao gerar hash: {str(e)}"
        )


# ============================================================================
# ESTRATÉGIAS DE RESOLUÇÃO
# ============================================================================

@router.get("/estrategias", response_model=Dict)
def obter_estrategias():
    """Retorna estratégias de resolução de conflitos disponíveis"""
    estrategias = [e.value for e in EstrategiaResolucao]

    return {
        "ok": True,
        "estrategias": estrategias,
        "descricoes": {
            "local_vence": "Versão local prevalece",
            "remoto_vence": "Versão remota prevalece",
            "merge_timestamps": "Versão mais recente prevalece",
            "manual": "Requer decisão manual"
        }
    }
