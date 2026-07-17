"""
Serviço de leitura de arquivos Access (.mdb) via mdbtools.
Funciona em Linux/Docker (mesmo comportamento em hosts Windows e Linux,
pois o container é sempre Linux).

Requer o pacote 'mdbtools' instalado no container (ver Dockerfile).
"""

import os
import csv
import io
import subprocess
from typing import List, Dict, Optional


# Diretório onde a pasta de .mdb é montada dentro do container (ver docker-compose).
MDB_DIR = os.environ.get("MDB_DIR", "/dados_mdb")


class MdbService:
    """Lê pastas e arquivos Access (.mdb) usando mdbtools."""

    @staticmethod
    def _seguro(caminho: str) -> str:
        """Impede sair da pasta montada (path traversal)."""
        base = os.path.realpath(MDB_DIR)
        alvo = os.path.realpath(os.path.join(base, caminho))
        if not alvo.startswith(base):
            raise ValueError("Caminho fora da pasta permitida")
        return alvo

    @staticmethod
    def mdbtools_disponivel() -> bool:
        """Verifica se o mdbtools está instalado."""
        try:
            subprocess.run(["mdb-ver", "--help"], capture_output=True, timeout=5)
            return True
        except Exception:
            try:
                subprocess.run(["mdb-tables", "--help"], capture_output=True, timeout=5)
                return True
            except Exception:
                return False

    @staticmethod
    def escanear(subpasta: str = "") -> Dict:
        """
        Lista os arquivos .mdb (e subpastas) dentro da pasta montada.

        Args:
            subpasta: caminho relativo dentro de MDB_DIR (ex.: "Backup 02.01.2026")

        Returns:
            Dict com pasta atual, subpastas e arquivos .mdb encontrados
        """
        base = MdbService._seguro(subpasta) if subpasta else os.path.realpath(MDB_DIR)

        if not os.path.isdir(base):
            return {
                "ok": False,
                "erro": f"Pasta não encontrada: {MDB_DIR}. Configure MDB_PATH no .env e reconstrua.",
                "mdb_dir": MDB_DIR,
                "arquivos": [],
                "subpastas": [],
            }

        arquivos = []
        subpastas = []
        for nome in sorted(os.listdir(base)):
            caminho = os.path.join(base, nome)
            if os.path.isdir(caminho):
                subpastas.append(nome)
            elif nome.lower().endswith(".mdb"):
                try:
                    tamanho = os.path.getsize(caminho)
                except OSError:
                    tamanho = 0
                arquivos.append({"nome": nome, "tamanho": tamanho})

        return {
            "ok": True,
            "pasta_atual": subpasta or "/",
            "mdb_dir": MDB_DIR,
            "total_mdb": len(arquivos),
            "arquivos": arquivos,
            "subpastas": subpastas,
        }

    @staticmethod
    def listar_tabelas(arquivo: str) -> Dict:
        """
        Lista as tabelas de um arquivo .mdb.

        Args:
            arquivo: caminho relativo do .mdb dentro de MDB_DIR
        """
        alvo = MdbService._seguro(arquivo)
        if not os.path.isfile(alvo):
            return {"ok": False, "erro": f"Arquivo não encontrado: {arquivo}"}

        try:
            res = subprocess.run(
                ["mdb-tables", "-1", alvo],
                capture_output=True, text=True, timeout=30
            )
            tabelas = [t for t in res.stdout.splitlines() if t.strip()]
            return {"ok": True, "arquivo": arquivo, "tabelas": tabelas, "total": len(tabelas)}
        except Exception as e:
            return {"ok": False, "erro": f"Erro ao ler tabelas: {str(e)}"}

    @staticmethod
    def preview(arquivo: str, tabela: str, limite: int = 20) -> Dict:
        """
        Retorna as primeiras linhas de uma tabela de um .mdb.

        Args:
            arquivo: caminho relativo do .mdb
            tabela: nome da tabela
            limite: máximo de linhas a retornar
        """
        alvo = MdbService._seguro(arquivo)
        if not os.path.isfile(alvo):
            return {"ok": False, "erro": f"Arquivo não encontrado: {arquivo}"}

        try:
            res = subprocess.run(
                ["mdb-export", alvo, tabela],
                capture_output=True, text=True, timeout=60
            )
            if res.returncode != 0:
                return {"ok": False, "erro": res.stderr.strip() or "Falha ao exportar tabela"}

            leitor = csv.reader(io.StringIO(res.stdout))
            linhas = list(leitor)
            if not linhas:
                return {"ok": True, "arquivo": arquivo, "tabela": tabela, "colunas": [], "linhas": [], "total": 0}

            colunas = linhas[0]
            dados = linhas[1:limite + 1]
            return {
                "ok": True,
                "arquivo": arquivo,
                "tabela": tabela,
                "colunas": colunas,
                "linhas": dados,
                "total_amostra": len(dados),
                "total_colunas": len(colunas),
            }
        except Exception as e:
            return {"ok": False, "erro": f"Erro ao ler dados: {str(e)}"}

    @staticmethod
    def ler_tabela_completa(arquivo: str, tabela: str) -> List[Dict]:
        """
        Lê TODA uma tabela como lista de dicts (para importação).

        Args:
            arquivo: caminho relativo do .mdb
            tabela: nome da tabela
        """
        alvo = MdbService._seguro(arquivo)
        if not os.path.isfile(alvo):
            raise ValueError(f"Arquivo não encontrado: {arquivo}")

        res = subprocess.run(
            ["mdb-export", alvo, tabela],
            capture_output=True, text=True, timeout=300
        )
        if res.returncode != 0:
            raise ValueError(res.stderr.strip() or "Falha ao exportar tabela")

        leitor = csv.DictReader(io.StringIO(res.stdout))
        return list(leitor)
