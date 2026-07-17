"""
Leitura de arquivos Access (.mdb) em servidor remoto via SSH/SFTP.
Baixa o .mdb para um arquivo temporário e lê com mdbtools.
Permite acessar pastas na rede / outra máquina sem montar volume.
"""

import os
import csv
import io
import stat
import tempfile
import subprocess
from typing import Dict

try:
    import paramiko
    PARAMIKO_OK = True
except Exception:
    PARAMIKO_OK = False


class SshMdbService:
    """Acessa .mdb remotos via SFTP."""

    @staticmethod
    def _conectar(host: str, porta: int, usuario: str, senha: str):
        if not PARAMIKO_OK:
            raise RuntimeError("Biblioteca SSH (paramiko) não instalada")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=host,
            port=int(porta or 22),
            username=usuario,
            password=senha,
            timeout=10,
            allow_agent=False,
            look_for_keys=False,
        )
        return client

    @staticmethod
    def escanear(host: str, porta: int, usuario: str, senha: str, caminho: str) -> Dict:
        """Lista .mdb e subpastas de um caminho remoto via SFTP."""
        try:
            client = SshMdbService._conectar(host, porta, usuario, senha)
        except Exception as e:
            return {"ok": False, "erro": f"Falha na conexão SSH: {str(e)}"}

        try:
            sftp = client.open_sftp()
            caminho = caminho or "."
            itens = sftp.listdir_attr(caminho)
            arquivos, subpastas = [], []
            for it in itens:
                if stat.S_ISDIR(it.st_mode):
                    subpastas.append(it.filename)
                elif it.filename.lower().endswith(".mdb"):
                    arquivos.append({"nome": it.filename, "tamanho": it.st_size})
            return {
                "ok": True,
                "pasta_atual": caminho,
                "total_mdb": len(arquivos),
                "arquivos": sorted(arquivos, key=lambda x: x["nome"]),
                "subpastas": sorted(subpastas),
            }
        except Exception as e:
            return {"ok": False, "erro": f"Erro ao listar pasta remota: {str(e)}"}
        finally:
            client.close()

    @staticmethod
    def _baixar_temp(host, porta, usuario, senha, caminho, arquivo) -> str:
        """Baixa o .mdb remoto para um arquivo temporário local; retorna o caminho."""
        client = SshMdbService._conectar(host, porta, usuario, senha)
        try:
            sftp = client.open_sftp()
            remoto = f"{caminho.rstrip('/')}/{arquivo}" if caminho and caminho != "." else arquivo
            fd, local = tempfile.mkstemp(suffix=".mdb")
            os.close(fd)
            sftp.get(remoto, local)
            return local
        finally:
            client.close()

    @staticmethod
    def listar_tabelas(host, porta, usuario, senha, caminho, arquivo) -> Dict:
        try:
            local = SshMdbService._baixar_temp(host, porta, usuario, senha, caminho, arquivo)
        except Exception as e:
            return {"ok": False, "erro": f"Erro ao baixar arquivo: {str(e)}"}
        try:
            res = subprocess.run(["mdb-tables", "-1", local], capture_output=True, text=True, timeout=60)
            tabelas = [t for t in res.stdout.splitlines() if t.strip()]
            return {"ok": True, "arquivo": arquivo, "tabelas": tabelas, "total": len(tabelas)}
        except Exception as e:
            return {"ok": False, "erro": f"Erro ao ler tabelas: {str(e)}"}
        finally:
            try:
                os.remove(local)
            except OSError:
                pass

    @staticmethod
    def preview(host, porta, usuario, senha, caminho, arquivo, tabela, limite=20) -> Dict:
        try:
            local = SshMdbService._baixar_temp(host, porta, usuario, senha, caminho, arquivo)
        except Exception as e:
            return {"ok": False, "erro": f"Erro ao baixar arquivo: {str(e)}"}
        try:
            res = subprocess.run(["mdb-export", local, tabela], capture_output=True, text=True, timeout=120)
            if res.returncode != 0:
                return {"ok": False, "erro": res.stderr.strip() or "Falha ao exportar tabela"}
            linhas = list(csv.reader(io.StringIO(res.stdout)))
            if not linhas:
                return {"ok": True, "arquivo": arquivo, "tabela": tabela, "colunas": [], "linhas": [], "total_amostra": 0, "total_colunas": 0}
            colunas = linhas[0]
            dados = linhas[1:limite + 1]
            return {
                "ok": True, "arquivo": arquivo, "tabela": tabela,
                "colunas": colunas, "linhas": dados,
                "total_amostra": len(dados), "total_colunas": len(colunas),
            }
        except Exception as e:
            return {"ok": False, "erro": f"Erro ao ler dados: {str(e)}"}
        finally:
            try:
                os.remove(local)
            except OSError:
                pass
