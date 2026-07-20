"""
services/sync_terminais.py - Sincronização automática, bidirecional, entre terminais.

Ideia: cada terminal escreve o que tem num arquivo JSON (sync_<terminal>.json)
numa pasta compartilhada (rede) ou via SSH, e lê os arquivos dos outros
terminais, mesclando no banco local. Conflito = vence a edição mais recente
(updated_at). Funciona mesmo com o outro terminal desligado (fica no arquivo).

NÃO altera o fluxo de OS/Produtos/Clientes/Vendas; apenas lê e faz upsert.
"""

import os
import json
import stat
import tempfile
from datetime import datetime

from models import Cliente, Produto, Venda, VendaItem, MovimentoEstoque
from services.mdb_service import MDB_DIR

try:
    import paramiko
    PARAMIKO_OK = True
except Exception:
    PARAMIKO_OK = False

PREFIXO = "sync_"
SUFIXO = ".json"


# ============================================================
# Serialização (exportar o que este terminal tem)
# ============================================================
def _dt(v):
    return v.isoformat() if v else None


def _parse_dt(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def exportar_local(db) -> dict:
    """Monta o pacote de dados deste terminal (clientes, produtos, vendas)."""
    clientes = [{
        "codigo": c.codigo, "nome": c.nome, "endereco": c.endereco, "cidade": c.cidade,
        "cep": c.cep, "telefone": c.telefone, "email": c.email, "contato": c.contato,
        "ativo": c.ativo, "updated_at": _dt(c.updated_at),
    } for c in db.query(Cliente).all()]

    produtos = [{
        "codigo_barras": p.codigo_barras, "descricao": p.descricao, "unidade": p.unidade,
        "marca": p.marca, "preco_custo": p.preco_custo, "preco_venda": p.preco_venda,
        "estoque": p.estoque, "categoria": p.categoria, "status": p.status, "ncm": p.ncm,
        "ativo": p.ativo, "updated_at": _dt(p.updated_at),
    } for p in db.query(Produto).all()]

    vendas = [{
        "codigo": v.codigo, "vendedor": v.vendedor, "cliente_nome": v.cliente_nome,
        "pagamento": v.pagamento, "desconto": v.desconto, "valor_total": v.valor_total,
        "data": v.data.isoformat() if v.data else None, "hora": v.hora, "origem": v.origem,
        "updated_at": _dt(v.updated_at),
        "itens": [{
            "codigo_produto": it.codigo_produto, "descricao": it.descricao, "unidade": it.unidade,
            "quantidade": it.quantidade, "preco_unitario": it.preco_unitario, "subtotal": it.subtotal,
        } for it in v.itens],
    } for v in db.query(Venda).all()]

    movimentos = [{
        "uid": m.uid, "codigo_barras": m.codigo_barras, "tipo": m.tipo,
        "quantidade": m.quantidade, "delta": m.delta, "origem": m.origem,
        "referencia": m.referencia, "terminal_id": m.terminal_id, "observacao": m.observacao,
        "updated_at": _dt(m.updated_at),
    } for m in db.query(MovimentoEstoque).all()]

    return {
        "versao": 1,
        "gerado_em": datetime.utcnow().isoformat(),
        "clientes": clientes,
        "produtos": produtos,
        "vendas": vendas,
        "movimentos": movimentos,
    }


# ============================================================
# Aplicação (mesclar dados recebidos de outro terminal)
# ============================================================
def _mais_novo(incoming_dt, atual_dt) -> bool:
    """True se o registro recebido é mais recente (ou igual) que o local."""
    if incoming_dt is None:
        return False
    if atual_dt is None:
        return True
    return incoming_dt >= atual_dt


def _aplicar_movimentos(db, dados: dict) -> int:
    """
    Aplica os movimentos de estoque recebidos, atualizando o cache do produto.
      - eventos (venda/ajuste/entrada): append-only, dedup por uid, soma o delta.
      - baseline ('inicial', uid base:*): upsert com última edição; ajusta pela diferença.
    Produtos já foram criados na etapa anterior, então conseguimos localizá-los.
    """
    aplicados = 0
    for m in dados.get("movimentos", []):
        uid = m.get("uid")
        if not uid:
            continue
        cb = m.get("codigo_barras")
        delta = float(m.get("delta") or 0)
        inc_dt = _parse_dt(m.get("updated_at"))
        produto = None
        if cb:
            produto = db.query(Produto).filter(Produto.codigo_barras == cb).first()
        if produto is None:
            continue  # sem produto local para aplicar (ex.: sem código de barras)

        existente = db.query(MovimentoEstoque).filter(MovimentoEstoque.uid == uid).first()
        eh_baseline = (m.get("tipo") == "inicial") or uid.startswith("base:")

        if existente:
            if eh_baseline and _mais_novo(inc_dt, existente.updated_at):
                # ajusta o cache pela diferença da base
                produto.estoque = float(produto.estoque or 0) + (delta - float(existente.delta or 0))
                existente.delta = delta
                existente.quantidade = m.get("quantidade") or abs(delta)
                if inc_dt:
                    existente.updated_at = inc_dt
                db.add(existente)
                db.add(produto)
                aplicados += 1
            # eventos já existentes: nada a fazer (append-only)
            continue

        # novo movimento -> registra e aplica o delta ao cache
        novo = MovimentoEstoque(
            uid=uid, codigo_barras=cb, produto_id=produto.id, tipo=m.get("tipo"),
            quantidade=m.get("quantidade") or abs(delta), delta=delta,
            origem=m.get("origem"), referencia=m.get("referencia"),
            terminal_id=m.get("terminal_id"), observacao=m.get("observacao"),
        )
        if inc_dt:
            novo.updated_at = inc_dt
        db.add(novo)
        produto.estoque = float(produto.estoque or 0) + delta
        db.add(produto)
        aplicados += 1
    return aplicados


def aplicar_pacote(db, dados: dict) -> dict:
    """Faz upsert de clientes, produtos, vendas e movimentos recebidos. Retorna contagens."""
    res = {"clientes": 0, "produtos": 0, "vendas": 0, "movimentos": 0}

    # ---- Clientes (chave: codigo) ----
    for c in dados.get("clientes", []):
        cod = c.get("codigo")
        if cod is None:
            continue
        inc_dt = _parse_dt(c.get("updated_at"))
        existente = db.query(Cliente).filter(Cliente.codigo == cod).first()
        if existente:
            if _mais_novo(inc_dt, existente.updated_at):
                for campo in ("nome", "endereco", "cidade", "cep", "telefone", "email", "contato", "ativo"):
                    setattr(existente, campo, c.get(campo))
                if inc_dt:
                    existente.updated_at = inc_dt  # preserva LWW (evita ping-pong)
                db.add(existente)
                res["clientes"] += 1
        else:
            novo = Cliente(
                codigo=cod, nome=c.get("nome") or "(sem nome)", endereco=c.get("endereco"),
                cidade=c.get("cidade"), cep=c.get("cep"), telefone=c.get("telefone"),
                email=c.get("email"), contato=c.get("contato"),
                ativo=c.get("ativo", True),
            )
            if inc_dt:
                novo.updated_at = inc_dt
            db.add(novo)
            res["clientes"] += 1

    # ---- Produtos (chave: codigo_barras; ou descrição+marca se sem código) ----
    for p in dados.get("produtos", []):
        cb = p.get("codigo_barras")
        inc_dt = _parse_dt(p.get("updated_at"))
        if cb:
            existente = db.query(Produto).filter(Produto.codigo_barras == cb).first()
        else:
            existente = db.query(Produto).filter(
                Produto.codigo_barras.is_(None),
                Produto.descricao == p.get("descricao"),
                Produto.marca == p.get("marca"),
            ).first()
        if existente:
            if _mais_novo(inc_dt, existente.updated_at):
                # NÃO sincroniza 'estoque' aqui: quantidade é controlada por movimentos
                for campo in ("codigo_barras", "descricao", "unidade", "marca", "preco_custo",
                              "preco_venda", "categoria", "status", "ncm", "ativo"):
                    setattr(existente, campo, p.get(campo))
                if inc_dt:
                    existente.updated_at = inc_dt
                db.add(existente)
                res["produtos"] += 1
        else:
            # Produto novo entra com estoque 0; a quantidade é construída pelos movimentos
            novo = Produto(
                codigo_barras=cb, descricao=p.get("descricao") or "(sem descrição)",
                unidade=p.get("unidade"), marca=p.get("marca"),
                preco_custo=p.get("preco_custo") or 0, preco_venda=p.get("preco_venda") or 0,
                estoque=0, categoria=p.get("categoria"),
                status=p.get("status") or "ATIVO", ncm=p.get("ncm"), ativo=p.get("ativo", True),
            )
            if inc_dt:
                novo.updated_at = inc_dt
            db.add(novo)
            res["produtos"] += 1

    # ---- Vendas (append-only: cria se o número ainda não existe) ----
    for v in dados.get("vendas", []):
        cod = v.get("codigo")
        if not cod:
            continue
        if db.query(Venda).filter(Venda.codigo == cod).first():
            continue  # já existe (histórico é imutável) -> não duplica
        data = None
        if v.get("data"):
            try:
                data = datetime.fromisoformat(v["data"]).date()
            except (ValueError, TypeError):
                data = None
        nova = Venda(
            codigo=cod, vendedor=v.get("vendedor"), cliente_nome=v.get("cliente_nome"),
            pagamento=v.get("pagamento"), desconto=v.get("desconto") or 0,
            valor_total=v.get("valor_total") or 0, data=data, hora=v.get("hora"),
            origem=v.get("origem") or "importado",
        )
        for it in v.get("itens", []):
            nova.itens.append(VendaItem(
                codigo_produto=it.get("codigo_produto"), descricao=it.get("descricao") or "(sem descrição)",
                unidade=it.get("unidade"), quantidade=it.get("quantidade") or 0,
                preco_unitario=it.get("preco_unitario") or 0, subtotal=it.get("subtotal") or 0,
            ))
        db.add(nova)
        res["vendas"] += 1

    # ---- Movimentos de estoque (soma/subtrai; não sobrescreve) ----
    res["movimentos"] = _aplicar_movimentos(db, dados)

    db.commit()
    return res


# ============================================================
# Transporte: PASTA (rede/local montada)
# ============================================================
def _resolver_pasta(pasta_local: str) -> str:
    """Resolve o caminho da pasta compartilhada (relativo cai sob MDB_DIR)."""
    p = (pasta_local or "").strip()
    if not p:
        p = os.path.join(MDB_DIR, "sync")
    if not os.path.isabs(p):
        p = os.path.join(MDB_DIR, p)
    os.makedirs(p, exist_ok=True)
    return p


def _pasta_push(pasta: str, terminal_id: str, payload: dict):
    caminho = os.path.join(pasta, f"{PREFIXO}{terminal_id}{SUFIXO}")
    tmp = caminho + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    os.replace(tmp, caminho)  # escrita atômica


def _pasta_pull(pasta: str, terminal_id: str) -> list:
    pacotes = []
    for nome in os.listdir(pasta):
        if nome.startswith(PREFIXO) and nome.endswith(SUFIXO) and nome != f"{PREFIXO}{terminal_id}{SUFIXO}":
            try:
                with open(os.path.join(pasta, nome), "r", encoding="utf-8") as f:
                    pacotes.append((nome, json.load(f)))
            except Exception as e:
                print(f"⚠️  Falha lendo {nome}: {e}")
    return pacotes


# ============================================================
# Transporte: SSH/SFTP (outro PC)
# ============================================================
def _ssh_client(cfg):
    if not PARAMIKO_OK:
        raise RuntimeError("Biblioteca SSH (paramiko) não instalada")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=cfg.ssh_host, port=int(cfg.ssh_porta or 22), username=cfg.ssh_usuario,
        password=cfg.ssh_senha, timeout=10, allow_agent=False, look_for_keys=False,
    )
    return client


def _ssh_push_pull(cfg, terminal_id: str, payload: dict) -> list:
    client = _ssh_client(cfg)
    try:
        sftp = client.open_sftp()
        caminho = (cfg.ssh_caminho or ".").rstrip("/")
        base = caminho if caminho and caminho != "." else "."
        proprio = f"{base}/{PREFIXO}{terminal_id}{SUFIXO}" if base != "." else f"{PREFIXO}{terminal_id}{SUFIXO}"

        # PUSH: envia arquivo próprio
        fd, local_tmp = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        with open(local_tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
        sftp.put(local_tmp, proprio)
        os.remove(local_tmp)

        # PULL: lê arquivos dos outros terminais
        pacotes = []
        for it in sftp.listdir_attr(base):
            nome = it.filename
            if stat.S_ISDIR(it.st_mode):
                continue
            if nome.startswith(PREFIXO) and nome.endswith(SUFIXO) and nome != f"{PREFIXO}{terminal_id}{SUFIXO}":
                remoto = f"{base}/{nome}" if base != "." else nome
                fd, tmp = tempfile.mkstemp(suffix=".json")
                os.close(fd)
                try:
                    sftp.get(remoto, tmp)
                    with open(tmp, "r", encoding="utf-8") as f:
                        pacotes.append((nome, json.load(f)))
                except Exception as e:
                    print(f"⚠️  Falha SSH lendo {nome}: {e}")
                finally:
                    try:
                        os.remove(tmp)
                    except OSError:
                        pass
        return pacotes
    finally:
        client.close()


# ============================================================
# Orquestração
# ============================================================
def sincronizar(db, cfg) -> dict:
    """Executa um ciclo de sincronização (push + pull + merge)."""
    terminal_id = cfg.terminal_id or "terminal"
    payload = exportar_local(db)

    if cfg.modo == "ssh":
        pacotes = _ssh_push_pull(cfg, terminal_id, payload)
    else:
        pasta = _resolver_pasta(cfg.pasta_local)
        _pasta_push(pasta, terminal_id, payload)
        pacotes = _pasta_pull(pasta, terminal_id)

    total = {"clientes": 0, "produtos": 0, "vendas": 0, "movimentos": 0, "terminais": len(pacotes)}
    for _nome, dados in pacotes:
        r = aplicar_pacote(db, dados)
        total["clientes"] += r["clientes"]
        total["produtos"] += r["produtos"]
        total["vendas"] += r["vendas"]
        total["movimentos"] += r.get("movimentos", 0)

    return total
