"""
routes/ordens.py - CRUD de Ordens de Serviço
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from database import get_db
from models import OrdemServico, OrdemItem, Cliente
from schemas import OrdemServicioCreate, OrdemServicioUpdate, OrdemServicioResponse, OrdemItemCreate, MessageResponse

router = APIRouter()

# ===== LISTAR =====

@router.get("/", response_model=dict)
async def listar_ordens(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str = Query("", min_length=0),
    cliente_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """Lista ordens de serviço com filtros"""
    query = db.query(OrdemServico)
    
    if status:
        query = query.filter(OrdemServico.status == status)
    if cliente_id:
        query = query.filter(OrdemServico.cliente_id == cliente_id)
    
    total = query.count()
    # Ordenar por data_criacao (sempre preenchida) para não quebrar com data_abertura nula
    ordens = query.order_by(OrdemServico.id.desc()).offset(skip).limit(limit).all()

    # Montar items de forma robusta (não usa schema estrito que quebra com campos nulos)
    items = []
    for o in ordens:
        try:
            nome_cli = getattr(o, "nome_cliente", None)
            if not nome_cli and o.cliente:
                nome_cli = o.cliente.nome
            items.append({
                "id": o.id,
                "numero": o.numero,
                "numero_os": o.numero_os,
                "nome_cliente": nome_cli,
                "cliente_id": o.cliente_id,
                "status": o.status,
                "data_abertura": o.data_abertura.isoformat() if o.data_abertura else None,
                "data_criacao": o.data_criacao.isoformat() if o.data_criacao else None,
                "valor_total": float(o.valor_total or 0),
            })
        except Exception:
            continue

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items,
    }

@router.get("/{ordem_id}", response_model=OrdemServicioResponse)
async def obter_ordem(ordem_id: int, db: Session = Depends(get_db)):
    """Obtém detalhes de uma ordem"""
    ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
    if not ordem:
        raise HTTPException(status_code=404, detail="Ordem não encontrada")
    return OrdemServicioResponse.from_orm(ordem)

@router.get("/numero/{numero}", response_model=OrdemServicioResponse)
async def obter_ordem_por_numero(numero: int, db: Session = Depends(get_db)):
    """Obtém ordem por número"""
    ordem = db.query(OrdemServico).filter(OrdemServico.numero == numero).first()
    if not ordem:
        raise HTTPException(status_code=404, detail="Ordem não encontrada")
    return OrdemServicioResponse.from_orm(ordem)

# ===== CRIAR =====

@router.post("/", response_model=OrdemServicioResponse, status_code=201)
async def criar_ordem(ordem: OrdemServicioCreate, db: Session = Depends(get_db)):
    """Cria uma nova ordem de serviço"""
    # Validar cliente
    cliente = db.query(Cliente).filter(Cliente.id == ordem.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Validar número único
    existente = db.query(OrdemServico).filter(OrdemServico.numero == ordem.numero).first()
    if existente:
        raise HTTPException(status_code=400, detail="Número de OS já existe")
    
    nova_ordem = OrdemServico(**ordem.dict())
    db.add(nova_ordem)
    db.commit()
    db.refresh(nova_ordem)
    
    return OrdemServicioResponse.from_orm(nova_ordem)

# ===== ATUALIZAR =====

@router.put("/{ordem_id}", response_model=OrdemServicioResponse)
async def atualizar_ordem(
    ordem_id: int,
    ordem_update: OrdemServicioUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza uma ordem de serviço"""
    ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
    if not ordem:
        raise HTTPException(status_code=404, detail="Ordem não encontrada")
    
    dados = ordem_update.dict(exclude_unset=True)
    for chave, valor in dados.items():
        setattr(ordem, chave, valor)
    
    db.commit()
    db.refresh(ordem)
    
    return OrdemServicioResponse.from_orm(ordem)

# ===== DELETAR =====

@router.delete("/{ordem_id}", response_model=MessageResponse)
async def deletar_ordem(ordem_id: int, db: Session = Depends(get_db)):
    """Deleta uma ordem"""
    ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
    if not ordem:
        raise HTTPException(status_code=404, detail="Ordem não encontrada")
    
    db.delete(ordem)
    db.commit()
    
    return MessageResponse(message="Ordem deletada com sucesso")

# ===== ITENS DA ORDEM =====

@router.post("/{ordem_id}/itens", response_model=dict, status_code=201)
async def adicionar_item(ordem_id: int, item: OrdemItemCreate, db: Session = Depends(get_db)):
    """Adiciona um item a uma ordem"""
    ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
    if not ordem:
        raise HTTPException(status_code=404, detail="Ordem não encontrada")
    
    novo_item = OrdemItem(ordem_id=ordem_id, **item.dict())
    ordem.valor_total += item.valor_total
    
    db.add(novo_item)
    db.commit()
    db.refresh(novo_item)
    
    return {"id": novo_item.id, "message": "Item adicionado"}

@router.delete("/{ordem_id}/itens/{item_id}", response_model=MessageResponse)
async def remover_item(ordem_id: int, item_id: int, db: Session = Depends(get_db)):
    """Remove um item de uma ordem"""
    item = db.query(OrdemItem).filter(
        OrdemItem.id == item_id,
        OrdemItem.ordem_id == ordem_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    
    ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
    ordem.valor_total -= item.valor_total
    
    db.delete(item)
    db.commit()
    
    return MessageResponse(message="Item removido com sucesso")

# ===== ESTATÍSTICAS =====

@router.get("/stats/resumo", response_model=dict)
async def stats_ordens(db: Session = Depends(get_db)):
    """Estatísticas de ordens"""
    total_aberto = db.query(func.count(OrdemServico.id)).filter(
        OrdemServico.status == "aberto"
    ).scalar()
    total_fechado = db.query(func.count(OrdemServico.id)).filter(
        OrdemServico.status == "fechado"
    ).scalar()
    valor_total = db.query(func.sum(OrdemServico.valor_total)).scalar() or 0.0
    
    return {
        "total_aberto": total_aberto,
        "total_fechado": total_fechado,
        "valor_total": float(valor_total)
    }
