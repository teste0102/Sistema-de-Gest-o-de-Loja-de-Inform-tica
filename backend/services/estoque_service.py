"""
services/estoque_service.py - Estoque por movimentos (event-sourcing).

O estoque exibido (produto.estoque) é um cache atualizado a cada movimento.
A verdade é a soma dos deltas dos movimentos. Isso permite sincronizar vendas
dos dois terminais somando/subtraindo em vez de sobrescrever a contagem.
"""

import uuid
from datetime import datetime

from models import MovimentoEstoque, Produto


def terminal_id(db) -> str:
    """ID deste terminal (da configuração de sync)."""
    try:
        from models import SyncConfig
        cfg = db.query(SyncConfig).first()
        if cfg and cfg.terminal_id:
            return cfg.terminal_id
    except Exception:
        pass
    return "local"


def _uid_baseline(db, produto: Produto) -> str:
    """uid estável da contagem base (mesmo em todos os terminais quando há código)."""
    if produto.codigo_barras:
        return f"base:{produto.codigo_barras}"
    return f"base:{terminal_id(db)}:{produto.id}"


def registrar_movimento(db, produto: Produto, tipo: str, delta: float,
                        origem: str, referencia: str = None, observacao: str = None,
                        commit: bool = True) -> MovimentoEstoque:
    """Registra um evento de estoque (venda/ajuste/entrada) e atualiza o cache."""
    delta = float(delta or 0)
    mov = MovimentoEstoque(
        uid=f"{terminal_id(db)}:{uuid.uuid4().hex[:12]}",
        codigo_barras=produto.codigo_barras, produto_id=produto.id,
        tipo=tipo, quantidade=abs(delta), delta=delta,
        origem=origem, referencia=referencia, terminal_id=terminal_id(db),
        observacao=observacao,
    )
    db.add(mov)
    produto.estoque = float(produto.estoque or 0) + delta
    db.add(produto)
    if commit:
        db.commit()
    return mov


def definir_estoque(db, produto: Produto, novo_valor: float,
                    origem: str = "manual", commit: bool = True):
    """Ajusta o estoque para um valor absoluto registrando o movimento da diferença."""
    atual = float(produto.estoque or 0)
    delta = float(novo_valor or 0) - atual
    if delta == 0:
        return None
    tipo = "entrada" if delta > 0 else "saida"
    return registrar_movimento(
        db, produto, tipo, delta, origem,
        observacao=f"ajuste para {novo_valor}", commit=commit,
    )


def definir_baseline(db, produto: Produto, quantidade: float, commit: bool = True) -> MovimentoEstoque:
    """
    Define a contagem BASE do produto (importação / cadastro inicial).
    uid estável -> se o outro terminal importar o mesmo arquivo, não duplica.
    """
    uid = _uid_baseline(db, produto)
    novo_delta = float(quantidade or 0)
    mov = db.query(MovimentoEstoque).filter(MovimentoEstoque.uid == uid).first()
    if mov:
        # Ajusta o cache pela diferença da base (mantém os eventos de venda)
        produto.estoque = float(produto.estoque or 0) + (novo_delta - float(mov.delta or 0))
        mov.delta = novo_delta
        mov.quantidade = abs(novo_delta)
        mov.updated_at = datetime.utcnow()
        db.add(mov)
        db.add(produto)
    else:
        mov = MovimentoEstoque(
            uid=uid, codigo_barras=produto.codigo_barras, produto_id=produto.id,
            tipo="inicial", quantidade=abs(novo_delta), delta=novo_delta,
            origem="importacao", terminal_id=terminal_id(db),
        )
        db.add(mov)
        produto.estoque = novo_delta  # produto novo: base define o valor absoluto
        db.add(produto)
    if commit:
        db.commit()
    return mov


def backfill_baselines(db) -> int:
    """
    Cria os movimentos de base para produtos que ainda não têm nenhum, usando o
    estoque atual como contagem inicial. Idempotente. Roda uma vez no startup para
    que produtos já existentes também sincronizem o estoque corretamente.
    """
    criados = 0
    for p in db.query(Produto).all():
        uid = _uid_baseline(db, p)
        if not db.query(MovimentoEstoque).filter(MovimentoEstoque.uid == uid).first():
            db.add(MovimentoEstoque(
                uid=uid, codigo_barras=p.codigo_barras, produto_id=p.id,
                tipo="inicial", quantidade=abs(float(p.estoque or 0)),
                delta=float(p.estoque or 0), origem="backfill", terminal_id=terminal_id(db),
            ))
            criados += 1
    if criados:
        db.commit()
    return criados
