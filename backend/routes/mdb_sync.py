"""
Rotas para sincronização/leitura de arquivos Access (.mdb) do sistema antigo.
Usa mdbtools (ver services/mdb_service.py).
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict

from services.mdb_service import MdbService, MDB_DIR
from services.ssh_mdb_service import SshMdbService, PARAMIKO_OK

router = APIRouter(tags=["Sincronização MDB"])


# ===== SSH / Rede =====
class SshConn(BaseModel):
    host: str
    porta: int = 22
    usuario: str
    senha: str
    caminho: str = "."


class SshTabelas(SshConn):
    arquivo: str


class SshPreview(SshTabelas):
    tabela: str
    limite: int = 20


@router.get("/mdb/status", response_model=Dict)
def status_mdb():
    """Verifica se o mdbtools está disponível e onde a pasta está montada."""
    return {
        "ok": True,
        "mdbtools_disponivel": MdbService.mdbtools_disponivel(),
        "mdb_dir": MDB_DIR,
    }


@router.get("/mdb/escanear", response_model=Dict)
def escanear(subpasta: str = ""):
    """Lista os arquivos .mdb e subpastas dentro da pasta montada."""
    return MdbService.escanear(subpasta)


@router.get("/mdb/tabelas", response_model=Dict)
def listar_tabelas(arquivo: str):
    """Lista as tabelas de um arquivo .mdb."""
    return MdbService.listar_tabelas(arquivo)


@router.get("/mdb/preview", response_model=Dict)
def preview(arquivo: str, tabela: str, limite: int = 20):
    """Retorna as primeiras linhas de uma tabela do .mdb."""
    return MdbService.preview(arquivo, tabela, limite)


# ===== SSH / Rede =====

@router.get("/mdb/ssh/status", response_model=Dict)
def ssh_status():
    """Verifica se o SSH (paramiko) está disponível."""
    return {"ok": True, "ssh_disponivel": PARAMIKO_OK}


@router.post("/mdb/ssh/escanear", response_model=Dict)
def ssh_escanear(conn: SshConn):
    """Lista .mdb e subpastas de um servidor remoto via SSH/SFTP."""
    return SshMdbService.escanear(conn.host, conn.porta, conn.usuario, conn.senha, conn.caminho)


@router.post("/mdb/ssh/tabelas", response_model=Dict)
def ssh_tabelas(req: SshTabelas):
    """Lista as tabelas de um .mdb remoto (baixa via SFTP e lê com mdbtools)."""
    return SshMdbService.listar_tabelas(req.host, req.porta, req.usuario, req.senha, req.caminho, req.arquivo)


@router.post("/mdb/ssh/preview", response_model=Dict)
def ssh_preview(req: SshPreview):
    """Amostra de dados de uma tabela de um .mdb remoto."""
    return SshMdbService.preview(req.host, req.porta, req.usuario, req.senha, req.caminho, req.arquivo, req.tabela, req.limite)
