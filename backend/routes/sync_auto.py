"""
routes/sync_auto.py - Configuração e execução da sincronização automática
entre terminais (pasta na rede ou SSH). Bidirecional, last-write-wins.
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import SyncConfig
from services import sync_terminais

router = APIRouter(tags=["Sincronização Automática"])


class SyncConfigIn(BaseModel):
    modo: Optional[str] = None            # pasta | ssh
    pasta_local: Optional[str] = None
    ssh_host: Optional[str] = None
    ssh_porta: Optional[int] = None
    ssh_usuario: Optional[str] = None
    ssh_senha: Optional[str] = None
    ssh_caminho: Optional[str] = None
    intervalo_min: Optional[int] = None
    ativo: Optional[bool] = None
    terminal_id: Optional[str] = None


def obter_config(db: Session) -> SyncConfig:
    """Retorna a configuração (linha única), criando com terminal_id se não existir."""
    cfg = db.query(SyncConfig).first()
    if not cfg:
        cfg = SyncConfig(
            terminal_id=f"terminal-{uuid.uuid4().hex[:6]}",
            modo="pasta", intervalo_min=5, ativo=False, ssh_porta=22, ssh_caminho=".",
        )
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


def _config_dict(cfg: SyncConfig) -> dict:
    return {
        "terminal_id": cfg.terminal_id,
        "modo": cfg.modo,
        "pasta_local": cfg.pasta_local,
        "ssh_host": cfg.ssh_host,
        "ssh_porta": cfg.ssh_porta,
        "ssh_usuario": cfg.ssh_usuario,
        "ssh_senha": "***" if cfg.ssh_senha else None,  # nunca devolve a senha
        "ssh_caminho": cfg.ssh_caminho,
        "intervalo_min": cfg.intervalo_min,
        "ativo": cfg.ativo,
        "ultima_sync": cfg.ultima_sync.isoformat() if cfg.ultima_sync else None,
        "ultimo_status": cfg.ultimo_status,
    }


@router.get("/config", response_model=dict)
def get_config(db: Session = Depends(get_db)):
    """Obtém a configuração da sincronização automática."""
    return {"ok": True, "config": _config_dict(obter_config(db))}


@router.put("/config", response_model=dict)
def put_config(dados: SyncConfigIn, db: Session = Depends(get_db)):
    """Atualiza a configuração (apenas os campos enviados)."""
    cfg = obter_config(db)
    campos = dados.dict(exclude_unset=True)
    for chave, valor in campos.items():
        # não sobrescreve a senha com o placeholder "***"
        if chave == "ssh_senha" and valor in ("***", None, ""):
            continue
        setattr(cfg, chave, valor)
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return {"ok": True, "config": _config_dict(cfg)}


@router.post("/agora", response_model=dict)
def sincronizar_agora(db: Session = Depends(get_db)):
    """Executa uma sincronização imediatamente (push + pull + merge)."""
    cfg = obter_config(db)
    try:
        total = sync_terminais.sincronizar(db, cfg)
        cfg.ultima_sync = datetime.utcnow()
        cfg.ultimo_status = (
            f"OK: {total['terminais']} terminal(is) — "
            f"clientes {total['clientes']}, produtos {total['produtos']}, "
            f"vendas {total['vendas']}, estoque {total.get('movimentos', 0)}"
        )
        db.add(cfg)
        db.commit()
        return {"ok": True, "resultado": total, "mensagem": cfg.ultimo_status}
    except Exception as e:
        cfg.ultimo_status = f"ERRO: {str(e)}"
        db.add(cfg)
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status", response_model=dict)
def status(db: Session = Depends(get_db)):
    """Status da última sincronização."""
    cfg = obter_config(db)
    return {
        "ok": True,
        "ativo": cfg.ativo,
        "intervalo_min": cfg.intervalo_min,
        "ultima_sync": cfg.ultima_sync.isoformat() if cfg.ultima_sync else None,
        "ultimo_status": cfg.ultimo_status,
        "terminal_id": cfg.terminal_id,
    }
