"""
Rotas para Gerenciamento de Fotos
Upload, organização e busca de imagens por tipo de dano
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Optional

from ..database import get_db
from ..models import OrdemServico
from ..services.numero_os_service import NumeroOSService
from ..services.foto_service import FotoService


router = APIRouter(
    prefix="/api/os",
    tags=["Fotos"]
)

foto_svc = FotoService()


# ============================================================================
# SCHEMAS
# ============================================================================

class FotoResponse(BaseModel):
    """Schema para resposta de foto"""
    id: str
    arquivo: str
    thumbnail: str
    mime_type: str
    hash: str
    tamanho: int
    descricao: str
    tipo_dano: Optional[str]
    data_upload: str


# ============================================================================
# UPLOAD DE FOTO
# ============================================================================

@router.post("/{ordem_id}/fotos/upload", response_model=Dict)
async def upload_foto(
    ordem_id: int,
    arquivo: UploadFile = File(...),
    descricao: str = Form(""),
    tipo_dano: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload de foto para Ordem de Serviço

    Args:
        ordem_id: ID da ordem
        arquivo: Arquivo de imagem (JPEG, PNG, WebP)
        descricao: Descrição da foto
        tipo_dano: Tipo de dano (tela, botão, água, etc)
        db: Sessão de banco de dados

    Returns:
        Dict com informações da foto armazenada

    Raises:
        404: Se OS não encontrada
        400: Se arquivo inválido
    """
    try:
        # Verificar se OS existe
        ordem = NumeroOSService.obter_os_por_id(db, ordem_id)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        # Validar tipo de dano se informado
        if tipo_dano and not foto_svc.validar_tipo_dano(tipo_dano):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de dano inválido: {tipo_dano}"
            )

        # Ler conteúdo do arquivo
        conteudo = await arquivo.read()

        # Armazenar foto
        foto_meta = foto_svc.armazenar_foto(
            db=db,
            ordem_id=ordem_id,
            conteudo=conteudo,
            mime_type=arquivo.content_type,
            descricao=descricao,
            tipo_dano=tipo_dano
        )

        return {
            "ok": True,
            "foto": foto_meta,
            "ordem_id": ordem_id,
            "mensagem": "Foto armazenada com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao armazenar foto: {str(e)}"
        )


# ============================================================================
# LISTAR FOTOS
# ============================================================================

@router.get("/{ordem_id}/fotos", response_model=Dict)
def listar_fotos(
    ordem_id: int,
    tipo_dano: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista fotos de uma OS, opcionalmente filtradas por tipo de dano

    Args:
        ordem_id: ID da ordem
        tipo_dano: Filtrar por tipo de dano (opcional)
        db: Sessão de banco de dados

    Returns:
        Dict com lista de fotos

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

        fotos = foto_svc.listar_fotos(db, ordem_id, tipo_dano)

        return {
            "ok": True,
            "ordem_id": ordem_id,
            "total": len(fotos),
            "fotos": fotos,
            "filtro_tipo_dano": tipo_dano
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao listar fotos: {str(e)}"
        )


# ============================================================================
# OBTER INFORMAÇÕES DE FOTO
# ============================================================================

@router.get("/{ordem_id}/fotos/{foto_id}", response_model=Dict)
def obter_foto(
    ordem_id: int,
    foto_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtém informações de uma foto específica

    Args:
        ordem_id: ID da ordem
        foto_id: ID da foto
        db: Sessão de banco de dados

    Returns:
        Dict com metadados da foto

    Raises:
        404: Se OS ou foto não encontrada
    """
    try:
        ordem = NumeroOSService.obter_os_por_id(db, ordem_id)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        foto = foto_svc.obter_foto(db, ordem_id, foto_id)
        if not foto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Foto {foto_id} não encontrada"
            )

        return {
            "ok": True,
            "foto": foto
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao obter foto: {str(e)}"
        )


# ============================================================================
# DELETAR FOTO
# ============================================================================

@router.delete("/{ordem_id}/fotos/{foto_id}", response_model=Dict)
def deletar_foto(
    ordem_id: int,
    foto_id: str,
    db: Session = Depends(get_db)
):
    """
    Deleta foto de uma OS

    Args:
        ordem_id: ID da ordem
        foto_id: ID da foto
        db: Sessão de banco de dados

    Returns:
        Dict com confirmação

    Raises:
        404: Se OS ou foto não encontrada
    """
    try:
        ordem = NumeroOSService.obter_os_por_id(db, ordem_id)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        resultado = foto_svc.deletar_foto(db, ordem_id, foto_id)

        return resultado

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao deletar foto: {str(e)}"
        )


# ============================================================================
# TIPOS DE DANO
# ============================================================================

@router.get("/recursos/tipos-dano", response_model=Dict)
def obter_tipos_dano():
    """
    Retorna lista de tipos de dano suportados

    Returns:
        Dict com tipos de dano
    """
    tipos = foto_svc.obter_tipos_dano()

    return {
        "ok": True,
        "total": len(tipos),
        "tipos": tipos
    }
