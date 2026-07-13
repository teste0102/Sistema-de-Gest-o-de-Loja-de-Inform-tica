"""
routes/financeiro.py - CRUD de Lançamentos Financeiros
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime
from database import get_db
from models import Lancamento, Cliente, OrdemServico
from schemas import LancamentoCreate, LancamentoUpdate, LancamentoResponse, MessageResponse

router = APIRouter()

# ===== LISTAR =====

@router.get("/", response_model=dict)
async def listar_lancamentos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    tipo: str = Query("", min_length=0),  # receita, despesa
    data_inicio: date = Query(None),
    data_fim: date = Query(None),
    cliente_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """Lista lançamentos financeiros"""
    query = db.query(Lancamento)
    
    if tipo:
        query = query.filter(Lancamento.tipo == tipo)
    if data_inicio:
        query = query.filter(Lancamento.data >= data_inicio)
    if data_fim:
        query = query.filter(Lancamento.data <= data_fim)
    if cliente_id:
        query = query.filter(Lancamento.cliente_id == cliente_id)
    
    total = query.count()
    lancamentos = query.order_by(Lancamento.data.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [LancamentoResponse.from_orm(l) for l in lancamentos]
    }

@router.get("/{lancamento_id}", response_model=LancamentoResponse)
async def obter_lancamento(lancamento_id: int, db: Session = Depends(get_db)):
    """Obtém um lançamento"""
    lancamento = db.query(Lancamento).filter(Lancamento.id == lancamento_id).first()
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    return LancamentoResponse.from_orm(lancamento)

# ===== CRIAR =====

@router.post("/", response_model=LancamentoResponse, status_code=201)
async def criar_lancamento(lancamento: LancamentoCreate, db: Session = Depends(get_db)):
    """Cria um novo lançamento"""
    # Validar cliente se informado
    if lancamento.cliente_id:
        cliente = db.query(Cliente).filter(Cliente.id == lancamento.cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Validar ordem se informado
    if lancamento.ordem_id:
        ordem = db.query(OrdemServico).filter(OrdemServico.id == lancamento.ordem_id).first()
        if not ordem:
            raise HTTPException(status_code=404, detail="Ordem não encontrada")
    
    novo_lancamento = Lancamento(**lancamento.dict())
    db.add(novo_lancamento)
    db.commit()
    db.refresh(novo_lancamento)
    
    return LancamentoResponse.from_orm(novo_lancamento)

# ===== ATUALIZAR =====

@router.put("/{lancamento_id}", response_model=LancamentoResponse)
async def atualizar_lancamento(
    lancamento_id: int,
    lancamento_update: LancamentoUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um lançamento"""
    lancamento = db.query(Lancamento).filter(Lancamento.id == lancamento_id).first()
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    
    dados = lancamento_update.dict(exclude_unset=True)
    for chave, valor in dados.items():
        setattr(lancamento, chave, valor)
    
    db.commit()
    db.refresh(lancamento)
    
    return LancamentoResponse.from_orm(lancamento)

# ===== DELETAR =====

@router.delete("/{lancamento_id}", response_model=MessageResponse)
async def deletar_lancamento(lancamento_id: int, db: Session = Depends(get_db)):
    """Deleta um lançamento"""
    lancamento = db.query(Lancamento).filter(Lancamento.id == lancamento_id).first()
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    
    db.delete(lancamento)
    db.commit()
    
    return MessageResponse(message="Lançamento deletado com sucesso")

# ===== RELATÓRIOS =====

@router.get("/relatorio/saldo", response_model=dict)
async def relatorio_saldo(
    data_inicio: date = Query(None),
    data_fim: date = Query(None),
    db: Session = Depends(get_db)
):
    """Calcula saldo (receita - despesa)"""
    query_receita = db.query(func.sum(Lancamento.valor)).filter(Lancamento.tipo == "receita")
    query_despesa = db.query(func.sum(Lancamento.valor)).filter(Lancamento.tipo == "despesa")
    
    if data_inicio:
        query_receita = query_receita.filter(Lancamento.data >= data_inicio)
        query_despesa = query_despesa.filter(Lancamento.data >= data_inicio)
    if data_fim:
        query_receita = query_receita.filter(Lancamento.data <= data_fim)
        query_despesa = query_despesa.filter(Lancamento.data <= data_fim)
    
    receita = query_receita.scalar() or 0.0
    despesa = query_despesa.scalar() or 0.0
    saldo = receita - despesa
    
    return {
        "receita_total": float(receita),
        "despesa_total": float(despesa),
        "saldo": float(saldo),
        "periodo": {
            "inicio": data_inicio,
            "fim": data_fim
        }
    }

@router.get("/relatorio/por-categoria", response_model=dict)
async def relatorio_por_categoria(
    tipo: str = Query("receita"),
    data_inicio: date = Query(None),
    data_fim: date = Query(None),
    db: Session = Depends(get_db)
):
    """Agrupa lançamentos por categoria"""
    query = db.query(
        Lancamento.categoria,
        func.count(Lancamento.id).label("total_itens"),
        func.sum(Lancamento.valor).label("total_valor")
    ).filter(Lancamento.tipo == tipo)
    
    if data_inicio:
        query = query.filter(Lancamento.data >= data_inicio)
    if data_fim:
        query = query.filter(Lancamento.data <= data_fim)
    
    resultados = query.group_by(Lancamento.categoria).all()
    
    return {
        "tipo": tipo,
        "categorias": [
            {
                "categoria": r[0],
                "total_itens": r[1],
                "total_valor": float(r[2])
            }
            for r in resultados
        ]
    }

# ===== BAIXAR PAGAMENTO =====

@router.put("/{lancamento_id}/baixar", response_model=LancamentoResponse)
async def baixar_lancamento(lancamento_id: int, db: Session = Depends(get_db)):
    """Marca um lançamento como baixado/pago"""
    lancamento = db.query(Lancamento).filter(Lancamento.id == lancamento_id).first()
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    
    lancamento.baixado = True
    db.commit()
    db.refresh(lancamento)
    
    return LancamentoResponse.from_orm(lancamento)
