"""
Serviço de Laudo Técnico
Gerencia criação, assinatura digital e PDF de relatórios técnicos
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy.orm import Session
from backend.models import OrdemServico
from backend.utils.crypto_service import CryptoService


@dataclass
class DanoRegistro:
    """Registro de um dano identificado"""
    tipo: str
    descricao: str
    severidade: str  # leve, media, grave
    foto_ids: List[str]
    observacoes: Optional[str] = None


class LaudoService:
    """Serviço para gerenciar laudos técnicos de OS"""

    SEVERIDADES_VALIDAS = ["leve", "media", "grave"]
    TIPOS_DANO = [
        "tela", "botao", "bateria", "agua", "queda",
        "conector", "camera", "microfone", "falante", "vibracao", "outro"
    ]

    def __init__(self, crypto_service: CryptoService):
        """
        Inicializa serviço de laudo

        Args:
            crypto_service: Instância do CryptoService para assinaturas
        """
        self.crypto = crypto_service

    def validar_dano(self, tipo: str, descricao: str, severidade: str) -> Tuple[bool, str]:
        """
        Valida registro de dano

        Args:
            tipo: Tipo de dano
            descricao: Descrição do dano
            severidade: Nível de severidade

        Returns:
            Tupla (válido, mensagem)
        """
        if tipo not in self.TIPOS_DANO:
            return False, f"Tipo de dano inválido: {tipo}"

        if not descricao or len(descricao) < 5:
            return False, "Descrição deve ter pelo menos 5 caracteres"

        if severidade not in self.SEVERIDADES_VALIDAS:
            return False, f"Severidade inválida: {severidade}"

        return True, "Dano válido"

    def criar_laudo(
        self,
        db: Session,
        ordem_id: int,
        danos: List[Dict],
        observacoes_gerais: str = "",
        recomendacoes: List[str] = None,
        valor_conserto: Optional[float] = None
    ) -> Dict:
        """
        Cria laudo técnico para OS

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem
            danos: Lista de danos identificados
            observacoes_gerais: Observações gerais
            recomendacoes: Recomendações de reparo
            valor_conserto: Valor estimado do conserto

        Returns:
            Dict com dados do laudo criado

        Raises:
            ValueError: Se dados inválidos
        """
        # Obter OS
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem:
            raise ValueError(f"OS {ordem_id} não encontrada")

        # Validar danos
        for dano in danos:
            valido, msg = self.validar_dano(
                dano.get("tipo", ""),
                dano.get("descricao", ""),
                dano.get("severidade", "")
            )
            if not valido:
                raise ValueError(f"Dano inválido: {msg}")

        # Criar estrutura do laudo
        laudo_dados = {
            "ordem_id": ordem_id,
            "numero_os": ordem.numero_os,
            "marca": ordem.marca,
            "modelo": ordem.modelo,
            "imei": ordem.imei,
            "cliente_id": ordem.cliente_id,
            "data_criacao": datetime.now().isoformat(),
            "data_criacao_timestamp": int(datetime.now().timestamp()),
            "danos": danos,
            "total_danos": len(danos),
            "observacoes_gerais": observacoes_gerais,
            "recomendacoes": recomendacoes or [],
            "valor_conserto_estimado": valor_conserto,
            "status": "pendente_assinatura"
        }

        # Serializar para JSON
        laudo_json = json.dumps(laudo_dados, indent=2, ensure_ascii=False)

        # Assinar digitalmente (RSA-2048)
        assinatura = self.crypto.assinar_dados(laudo_json)

        # Armazenar na OS
        ordem.laudo_danos = danos
        ordem.laudo_data_criacao = datetime.now()
        ordem.laudo_assinatura_digital = assinatura

        db.add(ordem)
        db.commit()
        db.refresh(ordem)

        return {
            "ok": True,
            "ordem_id": ordem_id,
            "laudo_criado": True,
            "data_criacao": datetime.now().isoformat(),
            "total_danos": len(danos),
            "assinado": True,
            "mensagem": "Laudo criado com sucesso"
        }

    def obter_laudo(self, db: Session, ordem_id: int) -> Optional[Dict]:
        """
        Obtém laudo de uma OS

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem

        Returns:
            Dict com laudo ou None
        """
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem or not ordem.laudo_danos:
            return None

        return {
            "ordem_id": ordem_id,
            "numero_os": ordem.numero_os,
            "marca": ordem.marca,
            "modelo": ordem.modelo,
            "imei": ordem.imei,
            "danos": ordem.laudo_danos,
            "data_criacao": ordem.laudo_data_criacao.isoformat() if ordem.laudo_data_criacao else None,
            "assinado_cliente": ordem.laudo_assinado_cliente,
            "tem_assinatura_digital": ordem.laudo_assinatura_digital is not None
        }

    def validar_integridade_laudo(self, db: Session, ordem_id: int) -> Tuple[bool, str]:
        """
        Valida integridade do laudo (verifica assinatura digital)

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem

        Returns:
            Tupla (válido, mensagem)
        """
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem:
            return False, "OS não encontrada"

        if not ordem.laudo_assinatura_digital:
            return False, "Laudo não possui assinatura digital"

        if not ordem.laudo_danos:
            return False, "Laudo sem dados de danos"

        # Recriar JSON para validação
        laudo_dados = {
            "ordem_id": ordem_id,
            "numero_os": ordem.numero_os,
            "marca": ordem.marca,
            "modelo": ordem.modelo,
            "imei": ordem.imei,
            "danos": ordem.laudo_danos,
            "total_danos": len(ordem.laudo_danos) if ordem.laudo_danos else 0
        }

        laudo_json = json.dumps(laudo_dados, indent=2, ensure_ascii=False)

        # Validar assinatura
        try:
            assinatura_valida = self.crypto.validar_assinatura(
                laudo_json,
                ordem.laudo_assinatura_digital
            )
            if assinatura_valida:
                return True, "Laudo íntegro e válido"
            else:
                return False, "Assinatura digital inválida"
        except Exception as e:
            return False, f"Erro ao validar assinatura: {str(e)}"

    def registrar_assinatura_cliente(self, db: Session, ordem_id: int, dados_assinatura: str) -> Dict:
        """
        Registra assinatura do cliente (caneta USB)

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem
            dados_assinatura: Dados da assinatura capturada

        Returns:
            Dict com confirmação
        """
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem:
            raise ValueError(f"OS {ordem_id} não encontrada")

        if not ordem.laudo_assinatura_digital:
            raise ValueError("OS não possui laudo técnico")

        # Armazenar assinatura do cliente
        ordem.laudo_assinado_cliente = True
        db.add(ordem)
        db.commit()

        return {
            "ok": True,
            "ordem_id": ordem_id,
            "laudo_assinado_cliente": True,
            "data_assinatura": datetime.now().isoformat(),
            "mensagem": "Assinatura do cliente registrada com sucesso"
        }

    def gerar_resumo_laudo(self, db: Session, ordem_id: int) -> Dict:
        """
        Gera resumo textual do laudo

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem

        Returns:
            Dict com resumo formatado
        """
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem or not ordem.laudo_danos:
            return {}

        danos = ordem.laudo_danos if isinstance(ordem.laudo_danos, list) else []

        # Contar por severidade
        severidades = {}
        for dano in danos:
            sev = dano.get("severidade", "media")
            severidades[sev] = severidades.get(sev, 0) + 1

        # Contar por tipo
        tipos = {}
        for dano in danos:
            tipo = dano.get("tipo", "outro")
            tipos[tipo] = tipos.get(tipo, 0) + 1

        resumo = f"""
RESUMO DO LAUDO TÉCNICO
=======================
Ordem: {ordem.numero_os}
Marca: {ordem.marca}
Modelo: {ordem.modelo}
IMEI: {ordem.imei}

DANOS ENCONTRADOS: {len(danos)}

Por Severidade:
"""
        for sev, count in severidades.items():
            resumo += f"  - {sev.upper()}: {count}\n"

        resumo += "\nPor Tipo:\n"
        for tipo, count in tipos.items():
            resumo += f"  - {tipo.upper()}: {count}\n"

        resumo += f"""
Data do Laudo: {ordem.laudo_data_criacao.isoformat() if ordem.laudo_data_criacao else 'N/A'}
Assinado pelo Cliente: {'Sim' if ordem.laudo_assinado_cliente else 'Não'}
"""

        return {
            "ordem_id": ordem_id,
            "numero_os": ordem.numero_os,
            "resumo": resumo.strip(),
            "total_danos": len(danos),
            "severidades": severidades,
            "tipos": tipos
        }

    def deletar_laudo(self, db: Session, ordem_id: int) -> Dict:
        """
        Deleta laudo de uma OS

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem

        Returns:
            Dict com resultado
        """
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem:
            raise ValueError(f"OS {ordem_id} não encontrada")

        if not ordem.laudo_assinatura_digital:
            raise ValueError("Nenhum laudo para deletar")

        ordem.laudo_danos = None
        ordem.laudo_assinatura_digital = None
        ordem.laudo_data_criacao = None
        ordem.laudo_assinado_cliente = False

        db.add(ordem)
        db.commit()

        return {
            "ok": True,
            "mensagem": "Laudo deletado com sucesso",
            "aviso": "O laudo não pode ser recuperado"
        }


# ============================================================================
# TESTES RÁPIDOS
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE LAUDO TÉCNICO")
    print("=" * 60)

    crypto = CryptoService()
    laudo_svc = LaudoService(crypto)

    print("\n1. TIPOS DE DANO")
    tipos = laudo_svc.TIPOS_DANO
    print(f"  Total: {len(tipos)}")
    print(f"  Tipos: {', '.join(tipos[:5])}...")

    print("\n2. VALIDAÇÃO DE DANO")
    testes = [
        ("tela", "Tela com trincas", "grave", True),
        ("tela", "TT", "grave", False),
        ("invalido", "Teste", "leve", False),
    ]

    for tipo, desc, sev, esperado in testes:
        valido, msg = laudo_svc.validar_dano(tipo, desc, sev)
        status = "✓" if valido == esperado else "✗"
        print(f"  {status} {tipo}: {msg}")

    print("\n3. SEVERIDADES")
    print(f"  Severidades: {', '.join(laudo_svc.SEVERIDADES_VALIDAS)}")

    print("\n✅ Testes básicos concluídos")
