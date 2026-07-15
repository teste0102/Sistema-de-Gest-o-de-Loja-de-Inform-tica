"""
Serviço de Gerenciamento de Fotos
Upload, armazenamento e organização de imagens por cliente/OS
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import hashlib
from PIL import Image
import io

from sqlalchemy.orm import Session
from models import OrdemServico, Cliente
from utils.crypto_service import CryptoService


class FotoService:
    """Serviço para gerenciar fotos de OS"""

    TIPOS_DANO_PADRAO = [
        "tela",
        "botao",
        "bateria",
        "agua",
        "queda",
        "conector",
        "camera",
        "microfone",
        "falante",
        "vibracao",
        "outro"
    ]

    TIPOS_MIME_VALIDOS = ["image/jpeg", "image/png", "image/webp"]
    TAMANHO_MAXIMO_MB = 10

    def __init__(self, caminho_base: Optional[str] = None):
        """
        Inicializa serviço de fotos

        Args:
            caminho_base: Caminho base para armazenar fotos
        """
        self.caminho_base = caminho_base or "/data/fotos"
        Path(self.caminho_base).mkdir(parents=True, exist_ok=True)

    def obter_caminho_os(self, cliente_id: int, ordem_id: int) -> str:
        """
        Obtém caminho para armazenar fotos de uma OS

        Organização: /data/fotos/{cliente_id}/{ordem_id}/

        Args:
            cliente_id: ID do cliente
            ordem_id: ID da ordem

        Returns:
            Caminho completo para fotos da OS
        """
        caminho = Path(self.caminho_base) / str(cliente_id) / str(ordem_id)
        caminho.mkdir(parents=True, exist_ok=True)
        return str(caminho)

    def validar_arquivo(self, conteudo: bytes, mime_type: str) -> tuple[bool, str]:
        """
        Valida arquivo de imagem

        Args:
            conteudo: Conteúdo do arquivo
            mime_type: Tipo MIME

        Returns:
            Tupla (válido, mensagem)
        """
        if mime_type not in self.TIPOS_MIME_VALIDOS:
            return False, f"Tipo MIME inválido: {mime_type}"

        tamanho_mb = len(conteudo) / (1024 * 1024)
        if tamanho_mb > self.TAMANHO_MAXIMO_MB:
            return False, f"Arquivo maior que {self.TAMANHO_MAXIMO_MB}MB"

        try:
            img = Image.open(io.BytesIO(conteudo))
            img.verify()
            return True, "Arquivo válido"
        except Exception as e:
            return False, f"Arquivo inválido: {str(e)}"

    def gerar_thumbnail(self, conteudo: bytes, tamanho: tuple = (200, 200)) -> bytes:
        """
        Gera thumbnail de uma imagem

        Args:
            conteudo: Conteúdo da imagem
            tamanho: Tupla (largura, altura)

        Returns:
            Thumbnail em bytes
        """
        img = Image.open(io.BytesIO(conteudo))
        img.thumbnail(tamanho, Image.Resampling.LANCZOS)

        thumb_io = io.BytesIO()
        img.save(thumb_io, format="JPEG", quality=80)
        return thumb_io.getvalue()

    def gerar_hash_arquivo(self, conteudo: bytes) -> str:
        """
        Gera hash SHA-256 do arquivo

        Args:
            conteudo: Conteúdo do arquivo

        Returns:
            Hash hexadecimal
        """
        return hashlib.sha256(conteudo).hexdigest()

    def armazenar_foto(
        self,
        db: Session,
        ordem_id: int,
        conteudo: bytes,
        mime_type: str,
        descricao: str = "",
        tipo_dano: Optional[str] = None
    ) -> Dict:
        """
        Armazena foto em disco e registra metadados no BD

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem
            conteudo: Conteúdo da foto
            mime_type: Tipo MIME
            descricao: Descrição da foto
            tipo_dano: Tipo de dano (ex: tela, botão, água)

        Returns:
            Dict com informações da foto armazenada

        Raises:
            ValueError: Se arquivo inválido
        """
        # Obter OS
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem:
            raise ValueError(f"OS {ordem_id} não encontrada")

        # Validar arquivo
        valido, msg = self.validar_arquivo(conteudo, mime_type)
        if not valido:
            raise ValueError(msg)

        # Gerar hash e ID
        hash_foto = self.gerar_hash_arquivo(conteudo)
        foto_id = f"foto-{hash_foto[:12]}"

        # Gerar thumbnail
        thumbnail = self.gerar_thumbnail(conteudo)

        # Obter caminho
        caminho_os = self.obter_caminho_os(ordem.cliente_id, ordem_id)

        # Salvar arquivo principal
        extensao = mime_type.split("/")[1]
        nome_arquivo = f"{foto_id}.{extensao}"
        caminho_arquivo = os.path.join(caminho_os, nome_arquivo)

        with open(caminho_arquivo, "wb") as f:
            f.write(conteudo)

        # Salvar thumbnail
        nome_thumbnail = f"{foto_id}_thumb.jpg"
        caminho_thumbnail = os.path.join(caminho_os, nome_thumbnail)

        with open(caminho_thumbnail, "wb") as f:
            f.write(thumbnail)

        # Metadados
        foto_meta = {
            "id": foto_id,
            "arquivo": nome_arquivo,
            "thumbnail": nome_thumbnail,
            "mime_type": mime_type,
            "hash": hash_foto,
            "tamanho": len(conteudo),
            "descricao": descricao,
            "tipo_dano": tipo_dano,
            "data_upload": datetime.now().isoformat()
        }

        # Registrar no BD
        if ordem.fotos is None:
            ordem.fotos = []
        else:
            ordem.fotos = json.loads(ordem.fotos) if isinstance(ordem.fotos, str) else ordem.fotos

        ordem.fotos.append(foto_meta)
        db.add(ordem)
        db.commit()

        return foto_meta

    def obter_foto(self, db: Session, ordem_id: int, foto_id: str) -> Optional[Dict]:
        """
        Obtém metadados de uma foto

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem
            foto_id: ID da foto

        Returns:
            Dict com metadados ou None
        """
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem or not ordem.fotos:
            return None

        fotos = json.loads(ordem.fotos) if isinstance(ordem.fotos, str) else ordem.fotos
        for foto in fotos:
            if foto.get("id") == foto_id:
                return foto

        return None

    def listar_fotos(self, db: Session, ordem_id: int, tipo_dano: Optional[str] = None) -> List[Dict]:
        """
        Lista fotos de uma OS, opcionalmente filtradas por tipo de dano

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem
            tipo_dano: Filtrar por tipo de dano (opcional)

        Returns:
            Lista de fotos
        """
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem or not ordem.fotos:
            return []

        fotos = json.loads(ordem.fotos) if isinstance(ordem.fotos, str) else ordem.fotos

        if tipo_dano:
            fotos = [f for f in fotos if f.get("tipo_dano") == tipo_dano]

        return fotos

    def deletar_foto(self, db: Session, ordem_id: int, foto_id: str) -> Dict:
        """
        Deleta foto e arquivo

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem
            foto_id: ID da foto

        Returns:
            Dict com resultado
        """
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem:
            raise ValueError(f"OS {ordem_id} não encontrada")

        if not ordem.fotos:
            raise ValueError("Nenhuma foto para deletar")

        fotos = json.loads(ordem.fotos) if isinstance(ordem.fotos, str) else ordem.fotos
        foto_encontrada = None

        for i, foto in enumerate(fotos):
            if foto.get("id") == foto_id:
                foto_encontrada = foto
                fotos.pop(i)
                break

        if not foto_encontrada:
            raise ValueError(f"Foto {foto_id} não encontrada")

        # Deletar arquivos
        caminho_os = self.obter_caminho_os(ordem.cliente_id, ordem_id)
        try:
            arquivo_principal = os.path.join(caminho_os, foto_encontrada["arquivo"])
            arquivo_thumb = os.path.join(caminho_os, foto_encontrada["thumbnail"])

            if os.path.exists(arquivo_principal):
                os.remove(arquivo_principal)
            if os.path.exists(arquivo_thumb):
                os.remove(arquivo_thumb)
        except Exception as e:
            raise ValueError(f"Erro ao deletar arquivos: {str(e)}")

        # Atualizar BD
        ordem.fotos = fotos
        db.add(ordem)
        db.commit()

        return {
            "ok": True,
            "foto_id": foto_id,
            "mensagem": "Foto deletada com sucesso"
        }

    def obter_tipos_dano(self) -> List[str]:
        """Retorna lista de tipos de dano suportados"""
        return self.TIPOS_DANO_PADRAO

    def validar_tipo_dano(self, tipo: str) -> bool:
        """Valida se tipo de dano é reconhecido"""
        return tipo.lower() in self.TIPOS_DANO_PADRAO


# ============================================================================
# TESTES RÁPIDOS
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE FOTOS")
    print("=" * 60)

    svc = FotoService()

    print("\n1. TIPOS DE DANO")
    tipos = svc.obter_tipos_dano()
    print(f"  Total de tipos: {len(tipos)}")
    print(f"  Tipos: {', '.join(tipos)}")

    print("\n2. VALIDAÇÃO DE TIPOS")
    tipos_teste = ["tela", "agua", "invalido"]
    for tipo in tipos_teste:
        resultado = svc.validar_tipo_dano(tipo)
        print(f"  {tipo}: {'✓' if resultado else '✗'}")

    print("\n3. HASH DE ARQUIVO")
    conteudo_teste = b"dados de teste para foto"
    hash_teste = svc.gerar_hash_arquivo(conteudo_teste)
    print(f"  Hash: {hash_teste}")

    print("\n✅ Testes básicos concluídos")
