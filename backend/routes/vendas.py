"""
routes/vendas.py - Vendas (PDV) + importação do Access (VENDAS.MDB / tabela CADA)

Mapa decodificado (VENDAS.MDB -> tabela "CADA"), cada linha = 1 item; agrupa por CODIGO:
  CODIGO -> codigo (nº da venda)   VENDEDOR -> vendedor   PAGAMENTO -> pagamento
  DES -> desconto   VALOR -> valor_total   DATA -> data   HORA -> hora
  CLIENTE -> cliente_nome
  COD -> codigo_produto   PRODUTO -> descricao   UNIDADE -> unidade
  QTDA -> quantidade   VENDA -> preco_unitario   SUB -> subtotal
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

from database import get_db
from models import Venda, VendaItem, Produto
from services.mdb_service import MdbService
from services.ssh_mdb_service import SshMdbService

router = APIRouter(tags=["Vendas"])


# ===== Schemas =====
class VendaItemIn(BaseModel):
    produto_id: Optional[int] = None
    codigo_produto: Optional[str] = None
    descricao: str
    unidade: Optional[str] = None
    quantidade: float = 1.0
    preco_unitario: float = 0.0
    subtotal: float = 0.0


class VendaIn(BaseModel):
    vendedor: Optional[str] = None
    cliente_nome: Optional[str] = None
    cliente_id: Optional[int] = None
    pagamento: Optional[str] = None
    desconto: float = 0.0
    valor_total: float = 0.0
    itens: List[VendaItemIn] = []


class ImportarVendasMdb(BaseModel):
    arquivo: str = "VENDAS.MDB"
    tabela: str = "CADA"
    subpasta: str = ""


class ImportarVendasSsh(ImportarVendasMdb):
    host: str
    porta: int = 22
    usuario: str
    senha: str
    caminho: str = "."


def _num(valor) -> float:
    if valor is None:
        return 0.0
    s = str(valor).strip().replace("R$", "").replace(" ", "")
    if not s:
        return 0.0
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0


def _data(valor) -> Optional[date]:
    """Converte a data do Access (MM/DD/YY HH:MM:SS) para date."""
    if not valor:
        return None
    s = str(valor).strip().split(" ")[0]
    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


# ===== LISTAR / DETALHAR =====
@router.get("/", response_model=dict)
def listar_vendas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    busca: str = Query("", min_length=0),
    db: Session = Depends(get_db),
):
    """Lista vendas (cabeçalho)."""
    query = db.query(Venda)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            (Venda.codigo.ilike(termo)) |
            (Venda.cliente_nome.ilike(termo)) |
            (Venda.vendedor.ilike(termo))
        )
    total = query.count()
    vendas = query.order_by(Venda.id.desc()).offset(skip).limit(limit).all()
    items = [{
        "id": v.id,
        "codigo": v.codigo,
        "vendedor": v.vendedor,
        "cliente_nome": v.cliente_nome,
        "pagamento": v.pagamento,
        "desconto": float(v.desconto or 0),
        "valor_total": float(v.valor_total or 0),
        "data": v.data.isoformat() if v.data else None,
        "hora": v.hora,
        "origem": v.origem,
        "total_itens": len(v.itens),
    } for v in vendas]
    return {"total": total, "skip": skip, "limit": limit, "items": items}


@router.get("/{venda_id}", response_model=dict)
def obter_venda(venda_id: int, db: Session = Depends(get_db)):
    """Detalhe da venda com itens."""
    v = db.query(Venda).filter(Venda.id == venda_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return {
        "id": v.id, "codigo": v.codigo, "vendedor": v.vendedor, "cliente_nome": v.cliente_nome,
        "pagamento": v.pagamento, "desconto": float(v.desconto or 0), "valor_total": float(v.valor_total or 0),
        "data": v.data.isoformat() if v.data else None, "hora": v.hora, "origem": v.origem,
        "itens": [{
            "id": it.id, "codigo_produto": it.codigo_produto, "descricao": it.descricao,
            "unidade": it.unidade, "quantidade": float(it.quantidade or 0),
            "preco_unitario": float(it.preco_unitario or 0), "subtotal": float(it.subtotal or 0),
            "produto_id": it.produto_id,
        } for it in v.itens],
    }


# ===== CRIAR (PDV) =====
@router.post("/", response_model=dict, status_code=201)
def criar_venda(dados: VendaIn, db: Session = Depends(get_db)):
    """Cria uma venda nova (PDV). Baixa o estoque dos produtos vinculados."""
    # Próximo código sequencial de venda nova, prefixado pelo terminal para ser
    # único entre os terminais na sincronização (evita colisão de "V000001").
    maior = db.query(func.max(Venda.id)).scalar() or 0
    try:
        from models import SyncConfig
        cfg = db.query(SyncConfig).first()
        pref = (cfg.terminal_id if cfg and cfg.terminal_id else "local").replace("terminal-", "")
    except Exception:
        pref = "local"
    codigo = f"{pref}-V{int(maior) + 1:06d}"

    total_calc = 0.0
    v = Venda(
        codigo=codigo, vendedor=dados.vendedor, cliente_nome=dados.cliente_nome,
        cliente_id=dados.cliente_id, pagamento=dados.pagamento,
        desconto=dados.desconto or 0.0, data=date.today(),
        hora=datetime.now().strftime("%H:%M:%S"), origem="novo",
    )
    for it in dados.itens:
        sub = it.subtotal or (it.quantidade * it.preco_unitario)
        total_calc += sub
        v.itens.append(VendaItem(
            produto_id=it.produto_id, codigo_produto=it.codigo_produto,
            descricao=it.descricao, unidade=it.unidade, quantidade=it.quantidade,
            preco_unitario=it.preco_unitario, subtotal=sub,
        ))
        # Baixar estoque quando o produto está cadastrado
        if it.produto_id:
            p = db.query(Produto).filter(Produto.id == it.produto_id).first()
            if p and p.estoque is not None:
                p.estoque = float(p.estoque) - float(it.quantidade or 0)
                db.add(p)

    v.valor_total = dados.valor_total or max(total_calc - (dados.desconto or 0.0), 0.0)
    db.add(v)
    db.commit()
    db.refresh(v)
    return {"ok": True, "id": v.id, "codigo": v.codigo, "valor_total": float(v.valor_total or 0)}


@router.delete("/{venda_id}", response_model=dict)
def deletar_venda(venda_id: int, db: Session = Depends(get_db)):
    v = db.query(Venda).filter(Venda.id == venda_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    db.delete(v)
    db.commit()
    return {"ok": True}


# ===== IMPORTAR DO ACCESS (VENDAS.MDB) =====
def _gravar_vendas(db: Session, linhas: list) -> dict:
    """Agrupa linhas por CODIGO e grava cada venda com seus itens. Não duplica."""
    # Agrupar por número da venda
    grupos = {}
    for row in linhas:
        cod = (str(row.get("CODIGO")).strip() if row.get("CODIGO") is not None else "")
        grupos.setdefault(cod, []).append(row)

    criadas = ignoradas = 0
    for cod, rows in grupos.items():
        if not cod:
            continue
        # Idempotente: se a venda importada já existe, pula
        existe = db.query(Venda).filter(Venda.codigo == cod, Venda.origem == "importado").first()
        if existe:
            ignoradas += 1
            continue

        cab = rows[0]
        # Tentar vincular ao cliente cadastrado pelo nome
        cliente_nome = (str(cab.get("CLIENTE")).strip() if cab.get("CLIENTE") else None)
        v = Venda(
            codigo=cod,
            vendedor=(str(cab.get("VENDEDOR")).strip() if cab.get("VENDEDOR") else None),
            cliente_nome=cliente_nome,
            pagamento=(str(cab.get("PAGAMENTO")).strip() if cab.get("PAGAMENTO") else None),
            desconto=_num(cab.get("DES")),
            valor_total=_num(cab.get("VALOR")),
            data=_data(cab.get("DATA")),
            hora=(str(cab.get("HORA")).strip() if cab.get("HORA") else None),
            origem="importado",
        )
        for r in rows:
            cod_prod = (str(r.get("COD")).strip() if r.get("COD") else None)
            produto_id = None
            if cod_prod:
                p = db.query(Produto).filter(Produto.codigo_barras == cod_prod).first()
                produto_id = p.id if p else None
            v.itens.append(VendaItem(
                produto_id=produto_id,
                codigo_produto=cod_prod,
                descricao=(str(r.get("PRODUTO")).strip() if r.get("PRODUTO") else "(sem descrição)"),
                unidade=(str(r.get("UNIDADE")).strip() if r.get("UNIDADE") else None),
                quantidade=_num(r.get("QTDA")),
                preco_unitario=_num(r.get("VENDA")),
                subtotal=_num(r.get("SUB")),
            ))
        db.add(v)
        criadas += 1

    db.commit()
    return {"total_linhas": len(linhas), "total_vendas": len(grupos), "criadas": criadas, "ja_existentes": ignoradas}


@router.post("/importar-mdb", response_model=dict)
def importar_vendas_mdb(req: ImportarVendasMdb, db: Session = Depends(get_db)):
    """Importa vendas de um .mdb na pasta montada (rede/local)."""
    caminho = f"{req.subpasta.rstrip('/')}/{req.arquivo}" if req.subpasta else req.arquivo
    try:
        linhas = MdbService.ler_tabela_completa(caminho, req.tabela)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler {caminho}: {str(e)}")
    return {"ok": True, "arquivo": caminho, "tabela": req.tabela, **_gravar_vendas(db, linhas)}


@router.post("/importar-mdb-ssh", response_model=dict)
def importar_vendas_ssh(req: ImportarVendasSsh, db: Session = Depends(get_db)):
    """Importa vendas de um .mdb em outro computador da rede via SSH/SFTP."""
    try:
        linhas = SshMdbService.ler_tabela_completa(
            req.host, req.porta, req.usuario, req.senha, req.caminho, req.arquivo, req.tabela
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler {req.arquivo} via SSH: {str(e)}")
    return {"ok": True, "arquivo": req.arquivo, "host": req.host, "tabela": req.tabela, **_gravar_vendas(db, linhas)}


# ===== ESTATÍSTICAS =====
@router.get("/stats/resumo", response_model=dict)
def stats_vendas(db: Session = Depends(get_db)):
    total = db.query(func.count(Venda.id)).scalar() or 0
    faturamento = db.query(func.sum(Venda.valor_total)).scalar() or 0.0
    return {"total_vendas": total, "faturamento": float(faturamento)}
