"""
Rotas para Gerenciamento de Senhas (PIN, Padrão, Nenhuma)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime

from ..database import get_db
from ..models import OrdemServico
from ..services.numero_os_service import NumeroOSService
from ..services.senha_service import SenhaService
from ..utils.crypto_service import CryptoService


router = APIRouter(
    prefix="/api/os",
    tags=["Senhas"]
)


# ============================================================================
# SCHEMAS
# ============================================================================

class CriarSenhaRequest(BaseModel):
    """Schema para criar nova senha"""
    tipo: str  # "pin", "padrao", "nenhuma"
    valor: Optional[str] = None  # PIN em texto plano
    coordenadas: Optional[List[tuple]] = None  # Padrão: [(x,y), ...]
    tamanho_pin: Optional[int] = 4  # Tamanho do PIN (4-6)

    class Config:
        schema_extra = {
            "example": {
                "tipo": "pin",
                "valor": "1234",
                "tamanho_pin": 4
            }
        }


class AvaliarSenhaRequest(BaseModel):
    """Schema para avaliar força de senha"""
    tipo: str
    valor: Optional[str] = None
    coordenadas: Optional[List[tuple]] = None


# ============================================================================
# CRIAR SENHA
# ============================================================================

@router.post("/{ordem_id}/senhas", response_model=Dict)
def criar_senha(
    ordem_id: int,
    request: CriarSenhaRequest,
    db: Session = Depends(get_db)
):
    """
    Cria nova senha para Ordem de Serviço

    Suporta 3 tipos:
    1. PIN: 4-6 dígitos
    2. Padrão: Risco em grid
    3. Nenhuma: Telefone desbloqueado

    Args:
        ordem_id: ID da ordem
        request: Dados da senha
        db: Sessão de banco de dados

    Returns:
        Dict com ID da senha criada

    Raises:
        404: Se OS não encontrada
        400: Se tipo/dados inválidos
    """
    try:
        # Verificar se OS existe
        ordem = NumeroOSService.obter_os_por_id(db, ordem_id)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        # Inicializar serviços
        crypto = CryptoService()
        senha_svc = SenhaService(crypto)

        # Validar tipo
        if not senha_svc.validar_tipo_senha(request.tipo):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de senha inválido: {request.tipo}"
            )

        # Gerar ID da senha
        senha_id = senha_svc.gerar_id_senha()

        # Processar conforme tipo
        if request.tipo == "pin":
            if not request.valor:
                # Gerar PIN aleatório
                pin = senha_svc.gerar_pin(request.tamanho_pin or 4)
            else:
                pin = request.valor
                # Validar PIN
                if not pin.isdigit() or not (4 <= len(pin) <= 6):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="PIN deve ter 4-6 dígitos"
                    )

            # Criptografar PIN
            pin_cripto = senha_svc.criptografar_pin(pin)

            # Armazenar na ordem
            ordem.node_senha_id = senha_id
            ordem.senha_tipo = "pin"
            ordem.senha_cifrada = pin_cripto

        elif request.tipo == "padrao":
            if not request.coordenadas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Coordenadas obrigatórias para padrão"
                )

            # Validar coordenadas
            if not isinstance(request.coordenadas, list) or len(request.coordenadas) < 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Padrão deve ter pelo menos 3 pontos"
                )

            # Criptografar padrão
            padrao_cripto = senha_svc.criptografar_padrao(request.coordenadas)

            # Armazenar na ordem
            ordem.node_senha_id = senha_id
            ordem.senha_tipo = "padrao"
            ordem.senha_cifrada = padrao_cripto
            # Gerar imagem base64 simulada
            ordem.senha_imagem = f"data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."

        elif request.tipo == "nenhuma":
            # Nenhuma senha = telefone desbloqueado
            ordem.node_senha_id = senha_id
            ordem.senha_tipo = "nenhuma"
            ordem.senha_cifrada = "NENHUMA_CRIPTOGRAFIA"

        # Salvar ordem
        db.add(ordem)
        db.commit()
        db.refresh(ordem)

        return {
            "ok": True,
            "senha_id": senha_id,
            "tipo": request.tipo,
            "ordem_id": ordem_id,
            "data_criada": datetime.now().isoformat(),
            "mensagem": f"Senha {request.tipo} criada com sucesso"
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar senha: {str(e)}"
        )


# ============================================================================
# GERAR SENHA ALEATÓRIA
# ============================================================================

@router.post("/{ordem_id}/senhas/gerar", response_model=Dict)
def gerar_senha_aleatoria(
    ordem_id: int,
    tipo: str = "pin",
    tamanho: int = 4,
    db: Session = Depends(get_db)
):
    """
    Gera senha aleatória (PIN ou Padrão)

    Args:
        ordem_id: ID da ordem
        tipo: "pin" ou "padrao"
        tamanho: Tamanho do PIN (4-6) ou grid (2-5)
        db: Sessão de banco de dados

    Returns:
        Dict com senha gerada (valor em claro para primeiro acesso)

    Raises:
        404: Se OS não encontrada
        400: Se parâmetros inválidos
    """
    try:
        # Verificar se OS existe
        ordem = NumeroOSService.obter_os_por_id(db, ordem_id)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        # Inicializar serviços
        crypto = CryptoService()
        senha_svc = SenhaService(crypto)

        if tipo == "pin":
            valor_gerado = senha_svc.gerar_pin(tamanho)
            return {
                "ok": True,
                "tipo": "pin",
                "valor": valor_gerado,
                "tamanho": tamanho,
                "qualidade": senha_svc.avaliar_qualidade_pin(valor_gerado)
            }

        elif tipo == "padrao":
            padrao = senha_svc.gerar_padrao(tamanho, tamanho, "media")
            return {
                "ok": True,
                "tipo": "padrao",
                "coordenadas": padrao["coordenadas"],
                "dimensoes": f"{tamanho}x{tamanho}",
                "qualidade": senha_svc.avaliar_qualidade_padrao(len(padrao["coordenadas"]))
            }

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo inválido: {tipo}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao gerar senha: {str(e)}"
        )


# ============================================================================
# OBTER INFORMAÇÕES DA SENHA
# ============================================================================

@router.get("/{ordem_id}/senhas", response_model=Dict)
def obter_senha(
    ordem_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém informações da senha da OS (não retorna o valor real por segurança)

    Args:
        ordem_id: ID da ordem
        db: Sessão de banco de dados

    Returns:
        Dict com tipo, data criação, sem retornar valor real

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

        if not ordem.node_senha_id:
            return {
                "ok": True,
                "tem_senha": False,
                "mensagem": "Nenhuma senha criada para esta OS"
            }

        return {
            "ok": True,
            "tem_senha": True,
            "senha_id": ordem.node_senha_id,
            "tipo": ordem.senha_tipo,
            "data_criada": ordem.updated_at.isoformat() if ordem.updated_at else None,
            "mensagem_seguranca": "Senha criptografada no servidor. Valor não pode ser recuperado."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao obter senha: {str(e)}"
        )


# ============================================================================
# DELETAR SENHA
# ============================================================================

@router.delete("/{ordem_id}/senhas", response_model=Dict)
def deletar_senha(
    ordem_id: int,
    db: Session = Depends(get_db)
):
    """
    Deleta senha da OS (não pode ser recuperada após exclusão)

    Args:
        ordem_id: ID da ordem
        db: Sessão de banco de dados

    Returns:
        Dict com confirmação

    Raises:
        404: Se OS não encontrada
        400: Se não houver senha
    """
    try:
        ordem = NumeroOSService.obter_os_por_id(db, ordem_id)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        if not ordem.node_senha_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhuma senha para deletar"
            )

        # Deletar
        tipo_deletado = ordem.senha_tipo
        ordem.node_senha_id = None
        ordem.senha_tipo = None
        ordem.senha_cifrada = None
        ordem.senha_imagem = None

        db.add(ordem)
        db.commit()

        return {
            "ok": True,
            "mensagem": f"Senha {tipo_deletado} deletada permanentemente",
            "aviso": "A senha não pode ser recuperada"
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao deletar senha: {str(e)}"
        )


# ============================================================================
# AVALIAR FORÇA DE SENHA
# ============================================================================

@router.post("/{ordem_id}/senhas/avaliar", response_model=Dict)
def avaliar_forca_senha(
    ordem_id: int,
    request: AvaliarSenhaRequest
):
    """
    Avalia força/qualidade de uma senha antes de criar

    Args:
        ordem_id: ID da ordem
        request: Dados da senha a avaliar

    Returns:
        Dict com score, nível e dicas
    """
    try:
        crypto = CryptoService()
        senha_svc = SenhaService(crypto)

        if request.tipo == "pin" and request.valor:
            resultado = senha_svc.avaliar_qualidade_pin(request.valor)
        elif request.tipo == "padrao" and request.coordenadas:
            resultado = senha_svc.avaliar_qualidade_padrao(len(request.coordenadas))
        else:
            return {
                "ok": False,
                "erro": "Tipo ou dados inválidos"
            }

        return {
            "ok": True,
            "tipo": request.tipo,
            "score": resultado["score"],
            "nivel": resultado["nivel"],
            "dicas": resultado.get("dicas", [])
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao avaliar senha: {str(e)}"
        )
