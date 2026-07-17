"""
Rotas para sincronização/leitura de arquivos Access (.mdb) do sistema antigo.
Usa mdbtools (ver services/mdb_service.py).
"""

from fastapi import APIRouter
from typing import Dict

from services.mdb_service import MdbService, MDB_DIR

router = APIRouter(tags=["Sincronização MDB"])


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
