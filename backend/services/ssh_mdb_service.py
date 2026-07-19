"""
Leitura de arquivos Access (.mdb) em servidor remoto via SSH/SFTP.
Baixa o .mdb para um arquivo temporário e lê com mdbtools.
Permite acessar pastas na rede / outra máquina sem montar volume.
"""

import os
import csv
import io
import stat
import socket
import tempfile
import subprocess
import concurrent.futures
from typing import Dict, List

try:
    import paramiko
    PARAMIKO_OK = True
except Exception:
    PARAMIKO_OK = False


class SshMdbService:
    """Acessa .mdb remotos via SFTP."""

    @staticmethod
    def descobrir_rede(base: str, portas: List[int] = None) -> Dict:
        """
        Varre uma faixa da rede (base.1 a base.254) procurando hosts com
        portas abertas (SSH=22, compartilhamento Windows=445, RDP=3389).

        Args:
            base: prefixo da rede, ex.: "192.168.0"
            portas: portas a testar (padrão: 22 e 445)

        Returns:
            Dict com lista de hosts encontrados e portas abertas
        """
        base = (base or "").strip().rstrip(".")
        # aceitar tanto "192.168.0" quanto "192.168.0.0"
        partes = base.split(".")
        if len(partes) == 4:
            partes = partes[:3]
        if len(partes) != 3 or not all(p.isdigit() for p in partes):
            return {"ok": False, "erro": "Faixa inválida. Use algo como 192.168.0"}
        base3 = ".".join(partes)
        portas = portas or [22, 445]

        def checar(ip):
            abertas = []
            for p in portas:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.4)
                try:
                    if s.connect_ex((ip, p)) == 0:
                        abertas.append(p)
                except Exception:
                    pass
                finally:
                    s.close()
            return (ip, abertas)

        ips = [f"{base3}.{i}" for i in range(1, 255)]
        encontrados = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=120) as ex:
            for ip, abertas in ex.map(checar, ips):
                if abertas:
                    encontrados.append({
                        "ip": ip,
                        "portas": abertas,
                        "ssh": 22 in abertas,
                        "compartilhamento": 445 in abertas,
                    })
        return {"ok": True, "base": base3, "total": len(encontrados), "hosts": encontrados}

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
    def ler_tabela_completa(host, porta, usuario, senha, caminho, arquivo, tabela) -> List[Dict]:
        """Baixa o .mdb remoto e lê TODA uma tabela como lista de dicts (para importação)."""
        local = SshMdbService._baixar_temp(host, porta, usuario, senha, caminho, arquivo)
        try:
            res = subprocess.run(["mdb-export", local, tabela], capture_output=True, text=True, timeout=300)
            if res.returncode != 0:
                raise ValueError(res.stderr.strip() or "Falha ao exportar tabela")
            return list(csv.DictReader(io.StringIO(res.stdout)))
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
