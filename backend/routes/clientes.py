"""
routes/clientes.py - CRUD de Clientes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Cliente
from schemas import ClienteCreate, ClienteUpdate, ClienteResponse, MessageResponse

router = APIRouter()

# ===== LISTAR =====

@router.get("/", response_model=dict)
async def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    ativo: bool = Query(True),
    busca: str = Query("", min_length=0),
    db: Session = Depends(get_db)
):
    """Lista todos os clientes com paginação e filtro"""
    query = db.query(Cliente).filter(Cliente.ativo == ativo)
    
    if busca:
        query = query.filter(
            (Cliente.nome.ilike(f"%{busca}%")) |
            (Cliente.email.ilike(f"%{busca}%")) |
            (Cliente.telefone.ilike(f"%{busca}%"))
        )
    
    total = query.count()
    clientes = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [ClienteResponse.from_orm(c) for c in clientes]
    }

@router.get("/{cliente_id}", response_model=ClienteResponse)
async def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtém um cliente por ID"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return ClienteResponse.from_orm(cliente)

@router.get("/codigo/{codigo}", response_model=ClienteResponse)
async def obter_cliente_por_codigo(codigo: int, db: Session = Depends(get_db)):
    """Obtém um cliente por código"""
    cliente = db.query(Cliente).filter(Cliente.codigo == codigo).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return ClienteResponse.from_orm(cliente)

# ===== CRIAR =====

@router.post("/", response_model=ClienteResponse, status_code=201)
async def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Cria um novo cliente"""
    # Validar se código já existe
    existente = db.query(Cliente).filter(Cliente.codigo == cliente.codigo).first()
    if existente:
        raise HTTPException(status_code=400, detail="Código de cliente já existe")
    
    novo_cliente = Cliente(**cliente.dict())
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    
    return ClienteResponse.from_orm(novo_cliente)

# ===== ATUALIZAR =====

@router.put("/{cliente_id}", response_model=ClienteResponse)
async def atualizar_cliente(
    cliente_id: int,
    cliente_update: ClienteUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um cliente existente"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Atualizar apenas campos fornecidos
    dados = cliente_update.dict(exclude_unset=True)
    for chave, valor in dados.items():
        setattr(cliente, chave, valor)
    
    db.commit()
    db.refresh(cliente)
    
    return ClienteResponse.from_orm(cliente)

# ===== DELETAR =====

@router.delete("/{cliente_id}", response_model=MessageResponse)
async def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Deleta um cliente (soft delete - marca como inativo)"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    cliente.ativo = False
    db.commit()
    
    return MessageResponse(message="Cliente desativado com sucesso")

# ===== ESTATÍSTICAS =====

@router.get("/stats/total", response_model=dict)
async def stats_clientes(db: Session = Depends(get_db)):
    """Retorna estatísticas de clientes"""
    total_ativos = db.query(func.count(Cliente.id)).filter(Cliente.ativo == True).scalar()
    total_inativos = db.query(func.count(Cliente.id)).filter(Cliente.ativo == False).scalar()
    
    return {
        "total_ativos": total_ativos,
        "total_inativos": total_inativos,
        "total": total_ativos + total_inativos
    }
