"""
routes/produtos.py - CRUD de Produtos / Estoque + Importação do Access (ESTO.MDB)

Mapeamento decodificado do programa antigo (ESTO.MDB -> tabela "ESTO"):
    CODIGO -> codigo_barras     E5  -> descricao      E6  -> unidade
    E7     -> marca             E8  -> preco_custo    E22 -> preco_venda
    E30    -> estoque           S2  -> categoria      ST  -> status
    T2     -> ncm
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import Produto
from services.mdb_service import MdbService
from services.ssh_mdb_service import SshMdbService

router = APIRouter(tags=["Produtos / Estoque"])


# ===== Schemas =====
class ProdutoIn(BaseModel):
    codigo_barras: Optional[str] = None
    descricao: str
    unidade: Optional[str] = None
    marca: Optional[str] = None
    preco_custo: Optional[float] = 0.0
    preco_venda: Optional[float] = 0.0
    estoque: Optional[float] = 0.0
    categoria: Optional[str] = None
    status: Optional[str] = "ATIVO"
    ncm: Optional[str] = None
    ativo: Optional[bool] = True


class ImportarMdb(BaseModel):
    arquivo: str = "ESTO.MDB"
    tabela: str = "ESTO"
    subpasta: str = ""            # subpasta dentro da pasta montada (rede/local)


class ImportarMdbSsh(BaseModel):
    host: str
    porta: int = 22
    usuario: str
    senha: str
    caminho: str = "."           # pasta do .mdb no outro computador
    arquivo: str = "ESTO.MDB"
    tabela: str = "ESTO"


def _num(valor) -> float:
    """Converte um campo de texto do .mdb em float, tolerante a formatos."""
    if valor is None:
        return 0.0
    s = str(valor).strip()
    if not s:
        return 0.0
    # Remover símbolos e normalizar separador decimal
    s = s.replace("R$", "").replace(" ", "")
    if "," in s and "." in s:
        # Formato brasileiro 1.234,56 -> 1234.56
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0


def _dict_para_produto(row: dict) -> dict:
    """Mapeia uma linha da tabela ESTO para os campos do modelo Produto."""
    return {
        "codigo_barras": (row.get("CODIGO") or "").strip() or None,
        "descricao": (row.get("E5") or "").strip() or "(sem descrição)",
        "unidade": (row.get("E6") or "").strip() or None,
        "marca": (row.get("E7") or "").strip() or None,
        "preco_custo": _num(row.get("E8")),
        "preco_venda": _num(row.get("E22")),
        "estoque": _num(row.get("E30")),
        "categoria": (row.get("S2") or "").strip() or None,
        "status": (row.get("ST") or "").strip() or "ATIVO",
        "ncm": (row.get("T2") or "").strip() or None,
    }


# ===== LISTAR / BUSCAR =====
@router.get("/", response_model=dict)
def listar_produtos(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    busca: str = Query("", min_length=0),
    db: Session = Depends(get_db),
):
    """Lista produtos com busca por descrição, marca, categoria ou código de barras."""
    query = db.query(Produto)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(or_(
            Produto.descricao.ilike(termo),
            Produto.marca.ilike(termo),
            Produto.categoria.ilike(termo),
            Produto.codigo_barras.ilike(termo),
        ))
    total = query.count()
    produtos = query.order_by(Produto.descricao.asc()).offset(skip).limit(limit).all()
    items = [{
        "id": p.id,
        "codigo_barras": p.codigo_barras,
        "descricao": p.descricao,
        "unidade": p.unidade,
        "marca": p.marca,
        "preco_custo": float(p.preco_custo or 0),
        "preco_venda": float(p.preco_venda or 0),
        "estoque": float(p.estoque or 0),
        "categoria": p.categoria,
        "status": p.status,
        "ncm": p.ncm,
        "ativo": p.ativo,
    } for p in produtos]
    return {"total": total, "skip": skip, "limit": limit, "items": items}


@router.get("/barras/{codigo}", response_model=dict)
def buscar_por_codigo_barras(codigo: str, db: Session = Depends(get_db)):
    """Busca um produto pelo código de barras (para bipar no PDV)."""
    p = db.query(Produto).filter(Produto.codigo_barras == codigo.strip()).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {
        "id": p.id, "codigo_barras": p.codigo_barras, "descricao": p.descricao,
        "unidade": p.unidade, "marca": p.marca, "preco_venda": float(p.preco_venda or 0),
        "preco_custo": float(p.preco_custo or 0), "estoque": float(p.estoque or 0),
        "categoria": p.categoria,
    }


# ===== CRIAR / ALTERAR / DELETAR =====
@router.post("/", response_model=dict, status_code=201)
def criar_produto(dados: ProdutoIn, db: Session = Depends(get_db)):
    """Cria um produto manualmente."""
    p = Produto(**dados.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"ok": True, "id": p.id}


@router.put("/{produto_id}", response_model=dict)
def alterar_produto(produto_id: int, dados: ProdutoIn, db: Session = Depends(get_db)):
    """Altera um produto existente."""
    p = db.query(Produto).filter(Produto.id == produto_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    for chave, valor in dados.dict(exclude_unset=True).items():
        setattr(p, chave, valor)
    db.commit()
    return {"ok": True, "id": p.id}


@router.delete("/{produto_id}", response_model=dict)
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    """Remove um produto."""
    p = db.query(Produto).filter(Produto.id == produto_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(p)
    db.commit()
    return {"ok": True}


# ===== IMPORTAR DO ACCESS (ESTO.MDB) =====
def _gravar_produtos(db: Session, linhas: list) -> dict:
    """Grava/atualiza produtos a partir das linhas lidas do .mdb (código de barras = chave)."""
    criados = 0
    atualizados = 0
    for row in linhas:
        dados = _dict_para_produto(row)
        cb = dados.get("codigo_barras")

        existente = None
        if cb:
            existente = db.query(Produto).filter(Produto.codigo_barras == cb).first()

        if existente:
            for chave, valor in dados.items():
                setattr(existente, chave, valor)
            db.add(existente)
            atualizados += 1
        else:
            db.add(Produto(**dados))
            criados += 1

    db.commit()
    return {"total_lidos": len(linhas), "criados": criados, "atualizados": atualizados}


@router.post("/importar-mdb", response_model=dict)
def importar_do_mdb(req: ImportarMdb, db: Session = Depends(get_db)):
    """
    Importa produtos de um .mdb na pasta montada (rede/local).
    'subpasta' permite escolher a pasta do outro computador compartilhada.
    Produtos existentes (mesmo código de barras) são ATUALIZADOS; novos são criados.
    """
    caminho = f"{req.subpasta.rstrip('/')}/{req.arquivo}" if req.subpasta else req.arquivo
    try:
        linhas = MdbService.ler_tabela_completa(caminho, req.tabela)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler {caminho}: {str(e)}")

    resultado = _gravar_produtos(db, linhas)
    return {"ok": True, "arquivo": caminho, "tabela": req.tabela, **resultado}


@router.post("/importar-mdb-ssh", response_model=dict)
def importar_do_mdb_ssh(req: ImportarMdbSsh, db: Session = Depends(get_db)):
    """
    Importa produtos de um .mdb em outro computador da rede via SSH/SFTP.
    Baixa o arquivo, lê a tabela e grava (mesma regra do local).
    """
    try:
        linhas = SshMdbService.ler_tabela_completa(
            req.host, req.porta, req.usuario, req.senha, req.caminho, req.arquivo, req.tabela
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler {req.arquivo} via SSH: {str(e)}")

    resultado = _gravar_produtos(db, linhas)
    return {"ok": True, "arquivo": req.arquivo, "host": req.host, "tabela": req.tabela, **resultado}


# ===== ESTATÍSTICAS =====
@router.get("/stats/resumo", response_model=dict)
def stats_produtos(db: Session = Depends(get_db)):
    """Resumo do estoque."""
    total = db.query(func.count(Produto.id)).scalar() or 0
    valor_estoque = db.query(
        func.sum(Produto.preco_custo * Produto.estoque)
    ).scalar() or 0.0
    sem_estoque = db.query(func.count(Produto.id)).filter(Produto.estoque <= 0).scalar() or 0
    return {
        "total_produtos": total,
        "valor_estoque_custo": float(valor_estoque),
        "sem_estoque": sem_estoque,
    }
