"""
routes/clientes.py - CRUD de Clientes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from database import get_db
from models import Cliente
from schemas import ClienteCreate, ClienteUpdate, ClienteResponse, MessageResponse
from services.mdb_service import MdbService
from services.ssh_mdb_service import SshMdbService

router = APIRouter()


# ===== IMPORTAÇÃO DO ACCESS (CADA.MDB / tabela CADA) =====
class ImportarClientesMdb(BaseModel):
    arquivo: str = "CADA.MDB"
    tabela: str = "CADA"
    subpasta: str = ""


class ImportarClientesSsh(ImportarClientesMdb):
    host: str
    porta: int = 22
    usuario: str
    senha: str
    caminho: str = "."


def _limpar(v):
    return (str(v).strip() if v is not None else "") or None


def _dict_para_cliente(row: dict) -> dict:
    """Mapeia uma linha da tabela CADA para os campos do modelo Cliente."""
    email = (_limpar(row.get("A15")) or "")
    # Só aceita email com formato mínimo válido (evita quebrar a listagem que valida EmailStr)
    email = email[:120] if ("@" in email and "." in email) else None
    return {
        "codigo": row.get("CODIGO"),
        "nome": _limpar(row.get("A1")) or "(sem nome)",
        "telefone": (_limpar(row.get("A4")) or "")[:15] or None,
        "contato": (_limpar(row.get("A8")) or "")[:60] or None,
        "endereco": (_limpar(row.get("A9")) or "")[:150] or None,
        "cidade": (_limpar(row.get("A12")) or "")[:80] or None,
        "cep": (_limpar(row.get("A14")) or "")[:10] or None,
        "email": email,
    }


def _gravar_clientes(db: Session, linhas: list) -> dict:
    """Grava/atualiza clientes (código = chave)."""
    criados = atualizados = 0
    maior = db.query(func.max(Cliente.codigo)).scalar() or 0
    for row in linhas:
        dados = _dict_para_cliente(row)
        # Normalizar código para inteiro sequencial
        try:
            cod = int(str(dados.get("codigo")).strip())
        except (ValueError, TypeError, AttributeError):
            maior += 1
            cod = maior
        dados["codigo"] = cod

        existente = db.query(Cliente).filter(Cliente.codigo == cod).first()
        if existente:
            for chave, valor in dados.items():
                if valor is not None:
                    setattr(existente, chave, valor)
            db.add(existente)
            atualizados += 1
        else:
            db.add(Cliente(ativo=True, **dados))
            criados += 1
    db.commit()
    return {"total_lidos": len(linhas), "criados": criados, "atualizados": atualizados}


@router.post("/importar-mdb", response_model=dict)
def importar_clientes_mdb(req: ImportarClientesMdb, db: Session = Depends(get_db)):
    """Importa clientes de um .mdb na pasta montada (rede/local)."""
    caminho = f"{req.subpasta.rstrip('/')}/{req.arquivo}" if req.subpasta else req.arquivo
    try:
        linhas = MdbService.ler_tabela_completa(caminho, req.tabela)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler {caminho}: {str(e)}")
    return {"ok": True, "arquivo": caminho, "tabela": req.tabela, **_gravar_clientes(db, linhas)}


@router.post("/importar-mdb-ssh", response_model=dict)
def importar_clientes_ssh(req: ImportarClientesSsh, db: Session = Depends(get_db)):
    """Importa clientes de um .mdb em outro computador da rede via SSH/SFTP."""
    try:
        linhas = SshMdbService.ler_tabela_completa(
            req.host, req.porta, req.usuario, req.senha, req.caminho, req.arquivo, req.tabela
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler {req.arquivo} via SSH: {str(e)}")
    return {"ok": True, "arquivo": req.arquivo, "host": req.host, "tabela": req.tabela, **_gravar_clientes(db, linhas)}

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
