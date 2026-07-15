"""
Rotas para Gerenciamento de Laudo Técnico
Criação, assinatura digital e PDF de relatórios técnicos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime

from backend.database import get_db
from backend.models import OrdemServico
from backend.services.numero_os_service import NumeroOSService
from backend.services.laudo_service import LaudoService
from backend.utils.crypto_service import CryptoService


router = APIRouter(
    prefix="/api/os",
    tags=["Laudo Técnico"]
)


# ============================================================================
# SCHEMAS
# ============================================================================

class DanoRequest(BaseModel):
    """Schema para registro de dano"""
    tipo: str  # tela, botao, bateria, agua, queda, etc
    descricao: str
    severidade: str  # leve, media, grave
    foto_ids: List[str] = []
    observacoes: Optional[str] = None


class CriarLaudoRequest(BaseModel):
    """Schema para criar laudo"""
    danos: List[DanoRequest]
    observacoes_gerais: str = ""
    recomendacoes: List[str] = []
    valor_conserto: Optional[float] = None


# ============================================================================
# CRIAR LAUDO
# ============================================================================

@router.post("/{ordem_id}/laudo", response_model=Dict)
def criar_laudo(
    ordem_id: int,
    request: CriarLaudoRequest,
    db: Session = Depends(get_db)
):
    """
    Cria laudo técnico para Ordem de Serviço

    Inclui:
    - Lista de danos identificados
    - Severidade de cada dano
    - Observações e recomendações
    - Assinatura digital RSA-2048

    Args:
        ordem_id: ID da ordem
        request: Dados do laudo
        db: Sessão de banco de dados

    Returns:
        Dict com dados do laudo criado

    Raises:
        404: Se OS não encontrada
        400: Se dados inválidos
    """
    try:
        # Verificar se OS existe
        ordem = NumeroOSService.obter_os_por_id(db, ordem_id)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        # Inicializar serviço
        crypto = CryptoService()
        laudo_svc = LaudoService(crypto)

        # Converter request para dicts
        danos = [d.dict() for d in request.danos]

        # Criar laudo
        resultado = laudo_svc.criar_laudo(
            db=db,
            ordem_id=ordem_id,
            danos=danos,
            observacoes_gerais=request.observacoes_gerais,
            recomendacoes=request.recomendacoes,
            valor_conserto=request.valor_conserto
        )

        return resultado

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar laudo: {str(e)}"
        )


# ============================================================================
# OBTER LAUDO
# ============================================================================

@router.get("/{ordem_id}/laudo", response_model=Dict)
def obter_laudo(
    ordem_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém laudo técnico de uma OS

    Args:
        ordem_id: ID da ordem
        db: Sessão de banco de dados

    Returns:
        Dict com dados do laudo

    Raises:
        404: Se OS ou laudo não encontrado
    """
    try:
        ordem = NumeroOSService.obter_os_por_id(db, ordem_id)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        crypto = CryptoService()
        laudo_svc = LaudoService(crypto)

        laudo = laudo_svc.obter_laudo(db, ordem_id)
        if not laudo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum laudo criado para esta OS"
            )

        return {
            "ok": True,
            "laudo": laudo
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao obter laudo: {str(e)}"
        )


# ============================================================================
# VALIDAR INTEGRIDADE DO LAUDO
# ============================================================================

@router.post("/{ordem_id}/laudo/validar", response_model=Dict)
def validar_laudo(
    ordem_id: int,
    db: Session = Depends(get_db)
):
    """
    Valida integridade do laudo (verifica assinatura digital)

    Args:
        ordem_id: ID da ordem
        db: Sessão de banco de dados

    Returns:
        Dict com resultado da validação

    Raises:
        404: Se OS não encontrada
    """
    try:
        ordem = NumeroOSService.obter_os_por_id(db, ordem_id)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        crypto = CryptoService()
        laudo_svc = LaudoService(crypto)

        valido, mensagem = laudo_svc.validar_integridade_laudo(db, ordem_id)

        return {
            "ok": valido,
            "ordem_id": ordem_id,
            "valido": valido,
            "mensagem": mensagem
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao validar laudo: {str(e)}"
        )


# ============================================================================
# REGISTRAR ASSINATURA DO CLIENTE
# ============================================================================

@router.post("/{ordem_id}/laudo/assinar", response_model=Dict)
def assinar_laudo_cliente(
    ordem_id: int,
    dados_assinatura: str,
    db: Session = Depends(get_db)
):
    """
    Registra assinatura do cliente (capturada com caneta USB)

    Args:
        ordem_id: ID da ordem
        dados_assinatura: Dados da assinatura capturada
        db: Sessão de banco de dados

    Returns:
        Dict com confirmação

    Raises:
        404: Se OS não encontrada
        400: Se OS não tem laudo técnico
    """
    try:
        ordem = NumeroOSService.obter_os_por_id(db, ordem_id)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        crypto = CryptoService()
        laudo_svc = LaudoService(crypto)

        resultado = laudo_svc.registrar_assinatura_cliente(
            db=db,
            ordem_id=ordem_id,
            dados_assinatura=dados_assinatura
        )

        return resultado

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao assinar laudo: {str(e)}"
        )


# ============================================================================
# GERAR RESUMO DO LAUDO
# ============================================================================

@router.get("/{ordem_id}/laudo/resumo", response_model=Dict)
def obter_resumo_laudo(
    ordem_id: int,
    db: Session = Depends(get_db)
):
    """
    Gera resumo textual do laudo

    Args:
        ordem_id: ID da ordem
        db: Sessão de banco de dados

    Returns:
        Dict com resumo formatado

    Raises:
        404: Se OS não encontrada
    """
    try:
        ordem = NumeroOSService.obter_os_por_id(db, ordem_id)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        crypto = CryptoService()
        laudo_svc = LaudoService(crypto)

        resumo = laudo_svc.gerar_resumo_laudo(db, ordem_id)

        return {
            "ok": True,
            "resumo": resumo
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao gerar resumo: {str(e)}"
        )


# ============================================================================
# DELETAR LAUDO
# ============================================================================

@router.delete("/{ordem_id}/laudo", response_model=Dict)
def deletar_laudo(
    ordem_id: int,
    db: Session = Depends(get_db)
):
    """
    Deleta laudo de uma OS (não pode ser recuperado)

    Args:
        ordem_id: ID da ordem
        db: Sessão de banco de dados

    Returns:
        Dict com confirmação

    Raises:
        404: Se OS não encontrada
    """
    try:
        ordem = NumeroOSService.obter_os_por_id(db, ordem_id)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        crypto = CryptoService()
        laudo_svc = LaudoService(crypto)

        resultado = laudo_svc.deletar_laudo(db, ordem_id)

        return resultado

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao deletar laudo: {str(e)}"
        )


# ============================================================================
# RECURSOS
# ============================================================================

@router.get("/recursos/tipos-severidade", response_model=Dict)
def obter_tipos_severidade():
    """Retorna severidades disponíveis"""
    crypto = CryptoService()
    laudo_svc = LaudoService(crypto)

    return {
        "ok": True,
        "severidades": laudo_svc.SEVERIDADES_VALIDAS
    }


@router.get("/recursos/tipos-dano-laudo", response_model=Dict)
def obter_tipos_dano_laudo():
    """Retorna tipos de dano para laudo"""
    crypto = CryptoService()
    laudo_svc = LaudoService(crypto)

    return {
        "ok": True,
        "tipos": laudo_svc.TIPOS_DANO
    }
