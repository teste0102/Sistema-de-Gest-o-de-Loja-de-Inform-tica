"""
Rotas para Geração e Gerenciamento de Números de Ordem de Serviço
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime

from database import get_db
from models import OrdemServico, Cliente
from services.numero_os_service import NumeroOSService
from schemas import OrdemServicioResponse, OrdemWizardUpdate
from pydantic import BaseModel


router = APIRouter(
    tags=["Ordem de Serviço - Números"]
)


# ============================================================================
# GERAR NOVO NÚMERO OS
# ============================================================================

@router.post("/gerar-numero", response_model=Dict)
def gerar_numero_os(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """
    Gera novo número de Ordem de Serviço

    Formato: OS-YYYYMMDD-XXXXX
    Exemplo: OS-20260715-00001

    Args:
        cliente_id: ID do cliente
        db: Sessão de banco de dados

    Returns:
        Dict com numero_os, ordem_id, data_criacao

    Raises:
        404: Se cliente não encontrado
        400: Se erro ao gerar número
    """
    try:
        # Verificar se cliente existe; se não, usar o primeiro disponível
        # ou criar um cliente padrão (evita falhar o salvamento por falta de cliente)
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            cliente = db.query(Cliente).first()
        if not cliente:
            cliente = Cliente(codigo=1, nome="Cliente Padrão", ativo=True)
            db.add(cliente)
            db.commit()
            db.refresh(cliente)
        cliente_id = cliente.id

        # Gerar número OS
        numero_os = NumeroOSService.gerar_numero(db, cliente_id)

        # Próximo número inteiro sequencial (para compatibilidade com a lista de ordens)
        from sqlalchemy import func as _func
        maior = db.query(_func.max(OrdemServico.numero)).scalar() or 0
        proximo_numero = int(maior) + 1

        # Criar ordem de serviço com número OS
        nova_ordem = OrdemServico(
            cliente_id=cliente_id,
            numero=proximo_numero,
            numero_os=numero_os,
            status="aberta",
            data_abertura=datetime.now().date(),
            data_criacao=datetime.now()
        )

        db.add(nova_ordem)
        db.commit()
        db.refresh(nova_ordem)

        return {
            "ok": True,
            "numero_os": numero_os,
            "ordem_id": nova_ordem.id,
            "data_criacao": nova_ordem.data_criacao,
            "cliente_id": cliente_id,
            "status": nova_ordem.status
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao gerar número OS: {str(e)}"
        )


# ============================================================================
# LISTAR OS DO CLIENTE
# ============================================================================

@router.get("/cliente/{cliente_id}", response_model=Dict)
def listar_os_cliente(
    cliente_id: int,
    limite: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Lista todas as Ordens de Serviço de um cliente com paginação

    Args:
        cliente_id: ID do cliente
        limite: Máximo de resultados (padrão: 50)
        offset: Offset para paginação (padrão: 0)
        db: Sessão de banco de dados

    Returns:
        Dict com lista de OS e total
    """
    try:
        # Verificar se cliente existe
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente {cliente_id} não encontrado"
            )

        # Contar total
        total = NumeroOSService.contar_os_cliente(db, cliente_id)

        # Listar com paginação
        ordens = NumeroOSService.listar_os_cliente(
            db, cliente_id, limite, offset
        )

        return {
            "ok": True,
            "total": total,
            "limit": limite,
            "offset": offset,
            "ordens": [
                {
                    "id": os.id,
                    "numero_os": os.numero_os,
                    "status": os.status,
                    "data_criacao": os.data_criacao,
                    "cliente_id": os.cliente_id
                }
                for os in ordens
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao listar OS: {str(e)}"
        )


# ============================================================================
# BUSCAR OS POR NÚMERO
# ============================================================================

@router.get("/numero/{numero_os}", response_model=Dict)
def obter_os_por_numero(
    numero_os: str,
    db: Session = Depends(get_db)
):
    """
    Busca Ordem de Serviço pelo número

    Args:
        numero_os: Número OS (formato: OS-YYYYMMDD-XXXXX)
        db: Sessão de banco de dados

    Returns:
        Dict com dados completos da OS

    Raises:
        400: Se número inválido
        404: Se OS não encontrada
    """
    try:
        # Validar formato
        if not NumeroOSService.validar_numero(numero_os):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Número OS inválido: {numero_os}"
            )

        # Buscar
        ordem = NumeroOSService.obter_os_por_numero(db, numero_os)
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS {numero_os} não encontrada"
            )

        return {
            "ok": True,
            "id": ordem.id,
            "numero_os": ordem.numero_os,
            "cliente_id": ordem.cliente_id,
            "status": ordem.status,
            "data_criacao": ordem.data_criacao,
            "updated_at": ordem.updated_at
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar OS: {str(e)}"
        )


# ============================================================================
# BUSCAR OS POR ID
# ============================================================================

@router.get("/{ordem_id}", response_model=Dict)
def obter_os_por_id(
    ordem_id: int,
    db: Session = Depends(get_db)
):
    """
    Busca Ordem de Serviço pelo ID

    Args:
        ordem_id: ID da ordem
        db: Sessão de banco de dados

    Returns:
        Dict com dados completos da OS

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

        # Contar recursos associados (fotos armazenadas em coluna JSON)
        fotos_lista = ordem.fotos or []
        if isinstance(fotos_lista, str):
            import json as _json
            fotos_lista = _json.loads(fotos_lista)
        total_fotos = len(fotos_lista)

        # Recuperar a SENHA salva para exibir na edição (ferramenta interna da loja)
        senha_pin = None
        senha_pattern = None
        try:
            if ordem.senha_tipo == "pin" and ordem.senha_cifrada:
                from services.senha_service import SenhaService
                from utils.crypto_service import CryptoService
                senha_pin = SenhaService(CryptoService()).descriptografar_pin(ordem.senha_cifrada)
            elif ordem.senha_tipo == "padrao" and ordem.senha_imagem:
                import json as _json
                info = _json.loads(ordem.senha_imagem)
                senha_pattern = info.get("pattern")
        except Exception:
            pass

        return {
            "ok": True,
            "id": ordem.id,
            "numero_os": ordem.numero_os,
            "cliente_id": ordem.cliente_id,
            "status": ordem.status,
            "data_criacao": ordem.data_criacao,
            "updated_at": ordem.updated_at,
            "total_fotos": total_fotos,
            "tem_laudo": ordem.laudo_assinatura_digital is not None,
            "tem_replay": ordem.replay_dados is not None,
            # Senha (para edição)
            "senha_tipo": ordem.senha_tipo,
            "senha_pin": senha_pin,
            "senha_pattern": senha_pattern,
            # Produto
            "produto_tipo": ordem.produto_tipo,
            "produto_descricao": ordem.produto_descricao,
            "marca": ordem.marca,
            "modelo": ordem.modelo,
            "imei": ordem.imei,
            # Endereço / Contato
            "nome_cliente": ordem.nome_cliente,
            "endereco_rua": ordem.endereco_rua,
            "endereco_tipo": ordem.endereco_tipo,
            "endereco_complemento": ordem.endereco_complemento,
            "endereco_numero": ordem.endereco_numero,
            "bairro": ordem.bairro,
            "cidade_os": ordem.cidade_os,
            "telefone_contato": ordem.telefone_contato,
            # Problema
            "problema_descricao": ordem.problema_descricao,
            # Orçamento
            "valor_aprovado_estimado": ordem.valor_aprovado_estimado,
            "valor_aprovado_parcelas": ordem.valor_aprovado_parcelas,
            "valor_total_estimado": ordem.valor_total_estimado,
            "valor_total_parcelas": ordem.valor_total_parcelas,
            # Assinatura
            "tem_assinatura": ordem.assinatura_cliente is not None,
            "assinatura_cliente": ordem.assinatura_cliente,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar OS: {str(e)}"
        )


# ============================================================================
# VALIDAR NÚMERO OS
# ============================================================================

@router.post("/validar-numero", response_model=Dict)
def validar_numero(numero_os: str):
    """
    Valida formato de número OS

    Args:
        numero_os: Número a validar

    Returns:
        Dict com resultado
    """
    resultado = NumeroOSService.validar_numero(numero_os)

    if resultado:
        data = NumeroOSService.extrair_data_numero_os(numero_os)
        seq = NumeroOSService.extrair_sequencial_numero_os(numero_os)

        return {
            "ok": True,
            "valido": True,
            "numero_os": numero_os,
            "data": data,
            "sequencial": seq
        }
    else:
        return {
            "ok": False,
            "valido": False,
            "numero_os": numero_os,
            "mensagem": "Formato inválido (esperado: OS-YYYYMMDD-XXXXX)"
        }


# ============================================================================
# ALTERAR OS (assistente / função Alterar) - atualiza qualquer campo
# ============================================================================

@router.put("/{ordem_id}/completo", response_model=Dict)
def alterar_os_completo(
    ordem_id: int,
    dados: OrdemWizardUpdate,
    db: Session = Depends(get_db)
):
    """
    Altera qualquer campo da OS após o cadastro (função Alterar).

    Args:
        ordem_id: ID da ordem
        dados: Campos a atualizar (apenas os enviados são alterados)
        db: Sessão de banco de dados

    Returns:
        Dict com dados atualizados

    Raises:
        404: Se OS não encontrada
    """
    try:
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        # Atualizar apenas os campos enviados
        campos = dados.dict(exclude_unset=True)
        for chave, valor in campos.items():
            setattr(ordem, chave, valor)

        db.add(ordem)
        db.commit()
        db.refresh(ordem)

        return {
            "ok": True,
            "ordem_id": ordem.id,
            "numero_os": ordem.numero_os,
            "status": ordem.status,
            "mensagem": "OS alterada com sucesso",
            "campos_atualizados": list(campos.keys())
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao alterar OS: {str(e)}"
        )


# ============================================================================
# ASSINATURA DIGITAL DO CLIENTE (caneta USB / canvas)
# ============================================================================

class AssinaturaRequest(BaseModel):
    assinatura: str  # imagem base64 (data:image/png;base64,...)


@router.post("/{ordem_id}/assinatura", response_model=Dict)
def salvar_assinatura(
    ordem_id: int,
    request: AssinaturaRequest,
    db: Session = Depends(get_db)
):
    """
    Salva a assinatura digital do cliente (imagem base64).

    Args:
        ordem_id: ID da ordem
        request: Assinatura em base64
        db: Sessão de banco de dados

    Returns:
        Dict com confirmação

    Raises:
        404: Se OS não encontrada
        400: Se assinatura inválida
    """
    try:
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OS com ID {ordem_id} não encontrada"
            )

        if not request.assinatura or len(request.assinatura) < 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assinatura inválida ou vazia"
            )

        ordem.assinatura_cliente = request.assinatura
        db.add(ordem)
        db.commit()

        return {
            "ok": True,
            "ordem_id": ordem_id,
            "mensagem": "Assinatura do cliente salva com sucesso"
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao salvar assinatura: {str(e)}"
        )


# ============================================================================
# CONTAR OS DO CLIENTE
# ============================================================================

@router.get("/cliente/{cliente_id}/total", response_model=Dict)
def contar_os_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """
    Conta total de OS de um cliente

    Args:
        cliente_id: ID do cliente
        db: Sessão de banco de dados

    Returns:
        Dict com total
    """
    try:
        total = NumeroOSService.contar_os_cliente(db, cliente_id)

        return {
            "ok": True,
            "cliente_id": cliente_id,
            "total_os": total
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao contar OS: {str(e)}"
        )
