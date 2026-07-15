"""
Serviço de Geração e Validação de Números de Ordem de Serviço
Formato: OS-YYYYMMDD-XXXXX (sequencial diário)
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Dict
import re

from models import OrdemServico
from database import get_db


class NumeroOSService:
    """Serviço centralizado para números OS"""

    PREFIXO = "OS"
    SEPARADOR = "-"
    TAMANHO_SEQUENCIAL = 5  # XXXXX (00001-99999)

    @staticmethod
    def gerar_numero(db: Session, cliente_id: int) -> str:
        """
        Gera novo número OS único e sequencial

        Formato: OS-20260715-00001

        Args:
            db: Sessão de banco de dados
            cliente_id: ID do cliente

        Returns:
            Número OS gerado

        Raises:
            ValueError: Se não conseguir gerar número único após tentativas
        """
        try:
            # Obter data atual no formato YYYYMMDD
            data_hoje = datetime.now().strftime("%Y%m%d")

            # Buscar último número gerado hoje
            ultima_ordem = db.query(OrdemServico).filter(
                func.substr(OrdemServico.numero_os, 1, 11) == f"{NumeroOSService.PREFIXO}{NumeroOSService.SEPARADOR}{data_hoje}",
                OrdemServico.cliente_id == cliente_id
            ).order_by(OrdemServico.numero_os.desc()).first()

            # Calcular próximo sequencial
            if ultima_ordem and ultima_ordem.numero_os:
                # Extrair sequencial: OS-20260715-00001 -> 00001
                partes = ultima_ordem.numero_os.split(NumeroOSService.SEPARADOR)
                if len(partes) >= 3:
                    sequencial_anterior = int(partes[2])
                    proximo_sequencial = sequencial_anterior + 1
                else:
                    proximo_sequencial = 1
            else:
                proximo_sequencial = 1

            # Validar se não ultrapassou limite diário (99999)
            if proximo_sequencial > 99999:
                raise ValueError(f"Limite de sequenciais para o dia {data_hoje} atingido")

            # Formatar número OS
            numero_os = f"{NumeroOSService.PREFIXO}{NumeroOSService.SEPARADOR}{data_hoje}{NumeroOSService.SEPARADOR}{proximo_sequencial:05d}"

            return numero_os

        except Exception as e:
            raise ValueError(f"Erro ao gerar número OS: {str(e)}")

    @staticmethod
    def validar_numero(numero_os: str) -> bool:
        """
        Valida formato de número OS

        Args:
            numero_os: Número a validar

        Returns:
            True se válido, False caso contrário
        """
        # Padrão: OS-YYYYMMDD-XXXXX
        padrao = r"^OS-\d{8}-\d{5}$"
        return bool(re.match(padrao, numero_os))

    @staticmethod
    def extrair_data_numero_os(numero_os: str) -> Optional[datetime]:
        """
        Extrai data do número OS

        Args:
            numero_os: Número OS

        Returns:
            Datetime da data extraída ou None se inválido
        """
        try:
            if not NumeroOSService.validar_numero(numero_os):
                return None

            # Extrair YYYYMMDD: OS-20260715-00001 -> 20260715
            partes = numero_os.split("-")
            data_str = partes[1]

            # Converter para datetime
            return datetime.strptime(data_str, "%Y%m%d")

        except Exception:
            return None

    @staticmethod
    def extrair_sequencial_numero_os(numero_os: str) -> Optional[int]:
        """
        Extrai número sequencial do número OS

        Args:
            numero_os: Número OS

        Returns:
            Sequencial ou None se inválido
        """
        try:
            if not NumeroOSService.validar_numero(numero_os):
                return None

            # Extrair XXXXX: OS-20260715-00001 -> 1
            partes = numero_os.split("-")
            return int(partes[2])

        except Exception:
            return None

    @staticmethod
    def converter_numero_para_id_numerico(numero_os: str) -> Optional[int]:
        """
        Converte número OS para ID numérico para uso interno

        Exemplo: OS-20260715-00001 -> 2602670150001 (compacto para BD)

        Args:
            numero_os: Número OS

        Returns:
            ID numérico ou None se inválido
        """
        try:
            if not NumeroOSService.validar_numero(numero_os):
                return None

            partes = numero_os.split("-")
            data = partes[1]  # YYYYMMDD
            seq = partes[2]   # XXXXX

            # Combinado: data + sequencial
            # Formato: YYYYMMDDXXXXX (13 dígitos)
            return int(f"{data}{seq}")

        except Exception:
            return None

    @staticmethod
    def gerar_numero_com_cliente(db: Session, cliente_id: int) -> Dict:
        """
        Gera número OS e retorna com informações completas

        Args:
            db: Sessão de banco de dados
            cliente_id: ID do cliente

        Returns:
            Dict com: numero_os, data_criacao, sequencial, valido
        """
        try:
            numero_os = NumeroOSService.gerar_numero(db, cliente_id)
            data = NumeroOSService.extrair_data_numero_os(numero_os)
            sequencial = NumeroOSService.extrair_sequencial_numero_os(numero_os)

            return {
                "numero_os": numero_os,
                "data_criacao": data,
                "sequencial": sequencial,
                "valido": True,
                "cliente_id": cliente_id
            }

        except Exception as e:
            raise ValueError(f"Erro ao gerar número OS: {str(e)}")

    @staticmethod
    def obter_numero_os_aleatorio_para_teste() -> str:
        """
        Gera número OS aleatório para testes (NÃO usa banco de dados)

        Returns:
            Número OS teste
        """
        from random import randint
        data = datetime.now().strftime("%Y%m%d")
        seq = randint(1, 99999)
        return f"OS-{data}-{seq:05d}"

    @staticmethod
    def listar_os_cliente(
        db: Session,
        cliente_id: int,
        limite: int = 50,
        offset: int = 0
    ) -> list:
        """
        Lista todas as OS de um cliente com paginação

        Args:
            db: Sessão de banco de dados
            cliente_id: ID do cliente
            limite: Número máximo de resultados
            offset: Offset para paginação

        Returns:
            Lista de OS
        """
        return db.query(OrdemServico).filter(
            OrdemServico.cliente_id == cliente_id
        ).order_by(
            OrdemServico.numero_os.desc()
        ).offset(offset).limit(limite).all()

    @staticmethod
    def contar_os_cliente(db: Session, cliente_id: int) -> int:
        """
        Conta quantas OS um cliente tem

        Args:
            db: Sessão de banco de dados
            cliente_id: ID do cliente

        Returns:
            Total de OS
        """
        return db.query(func.count(OrdemServico.id)).filter(
            OrdemServico.cliente_id == cliente_id
        ).scalar()

    @staticmethod
    def obter_os_por_numero(db: Session, numero_os: str) -> Optional[OrdemServico]:
        """
        Busca ordem de serviço pelo número

        Args:
            db: Sessão de banco de dados
            numero_os: Número OS

        Returns:
            OrdemServico ou None se não encontrada
        """
        return db.query(OrdemServico).filter(
            OrdemServico.numero_os == numero_os
        ).first()

    @staticmethod
    def obter_os_por_id(db: Session, ordem_id: int) -> Optional[OrdemServico]:
        """
        Busca ordem de serviço pelo ID

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem

        Returns:
            OrdemServico ou None se não encontrada
        """
        return db.query(OrdemServico).filter(
            OrdemServico.id == ordem_id
        ).first()


# ============================================================================
# TESTES RÁPIDOS
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE NÚMEROS OS")
    print("=" * 60)

    # Teste de validação
    numeros_teste = [
        "OS-20260715-00001",
        "OS-2026-0715-001",  # Inválido
        "OS-20260715-1",  # Inválido
        "OS-20261231-99999",  # Válido
    ]

    print("\nValidação de números:")
    for numero in numeros_teste:
        resultado = NumeroOSService.validar_numero(numero)
        print(f"  {numero}: {'✓ Válido' if resultado else '✗ Inválido'}")

    # Teste de extração
    numero_valido = "OS-20260715-00042"
    print(f"\nExtração de informações de {numero_valido}:")
    print(f"  Data: {NumeroOSService.extrair_data_numero_os(numero_valido)}")
    print(f"  Sequencial: {NumeroOSService.extrair_sequencial_numero_os(numero_valido)}")
    print(f"  ID Numérico: {NumeroOSService.converter_numero_para_id_numerico(numero_valido)}")

    # Teste de geração para testes
    print(f"\nNúmero OS de teste: {NumeroOSService.obter_numero_os_aleatorio_para_teste()}")
