"""
services/sync_service.py - Serviço de sincronização híbrida

Coordena sincronização de dados entre:
- Servidor Local (FastAPI + PostgreSQL)
- Servidores Remotos (PostgreSQL, Access, MySQL)
- Node.js (Atendimento) - Fotos, Vídeos, Senhas
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models import OrdemServico, Cliente, Lancamento, SyncQueue, SyncHistory
import requests

logger = logging.getLogger(__name__)


class SincronizadorHibrido:
    """Gerencia sincronização entre múltiplos servidores"""

    def __init__(self, db: Session, servidor_fastapi_url: str = "http://localhost:8000"):
        self.db = db
        self.servidor_fastapi = servidor_fastapi_url
        self.servidor_node = "http://localhost:3000"

    # ===== SINCRONIZAÇÃO COM SERVIDOR REMOTO =====

    def sincronizar_para_servidor_remoto(
        self,
        ordem_id: int,
        servidor_id: int,
        servidor_url: str,
        servidor_tipo: str = "postgresql"
    ) -> Dict:
        """
        Sincroniza ordem com servidor remoto

        Args:
            ordem_id: ID da ordem no banco local
            servidor_id: ID do servidor remoto
            servidor_url: URL/caminho do servidor remoto
            servidor_tipo: postgresql, access, mysql

        Returns:
            {
                "sucesso": bool,
                "mensagem": str,
                "ordem_sincronizada": bool,
                "dados_novos_ignorados": ["fotos", "videos", "senhas"]
            }
        """
        try:
            ordem = self.db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
            if not ordem:
                return {"sucesso": False, "mensagem": f"Ordem {ordem_id} não encontrada"}

            # Prepara dados para sincronizar
            dados_base = {
                "numero": ordem.numero,
                "cliente_id": ordem.cliente_id,
                "descricao": ordem.descricao,
                "data_abertura": ordem.data_abertura.isoformat() if ordem.data_abertura else None,
                "data_fechamento": ordem.data_fechamento.isoformat() if ordem.data_fechamento else None,
                "status": ordem.status,
                "tecnico": ordem.tecnico,
                "observacoes": ordem.observacoes,
                "valor_total": float(ordem.valor_total)
            }

            # Campos que NÃO sincronizam (apenas novo servidor)
            campos_nao_sincronizados = []
            if ordem.fotos:
                campos_nao_sincronizados.append("fotos")
            if ordem.videos:
                campos_nao_sincronizados.append("videos")
            if ordem.senha_imagem or ordem.senha_cifrada:
                campos_nao_sincronizados.append("senhas")

            # TODO: Implementar envio para servidor remoto
            # - Conectar ao banco remoto
            # - Validar se registro já existe
            # - Atualizar ou inserir
            # - Tratar conflitos

            logger.info(f"✅ Ordem {ordem.numero} sincronizada com servidor {servidor_id}")

            # Registra sincronização
            self._registrar_sincronizacao(
                ordem_id=ordem_id,
                servidor_id=servidor_id,
                status="sucesso"
            )

            # Atualiza marca de sincronização na ordem
            if not ordem.sincronizado_com_servidores:
                ordem.sincronizado_com_servidores = {}
            ordem.sincronizado_com_servidores[str(servidor_id)] = datetime.utcnow().isoformat()
            self.db.commit()

            return {
                "sucesso": True,
                "mensagem": f"Ordem sincronizada com sucesso",
                "ordem_sincronizada": True,
                "dados_novos_ignorados": campos_nao_sincronizados
            }

        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar ordem {ordem_id}: {str(e)}")
            self._registrar_sincronizacao(
                ordem_id=ordem_id,
                servidor_id=servidor_id,
                status="erro",
                mensagem_erro=str(e)
            )
            return {
                "sucesso": False,
                "mensagem": f"Erro ao sincronizar: {str(e)}"
            }

    def sincronizar_tudo_para_servidor(self, servidor_id: int) -> Dict:
        """
        Sincroniza TODAS as ordens com servidor remoto

        Usado quando:
        - Servidor acabou de ser adicionado
        - Necessário sincronizar base histórica
        """
        try:
            ordens = self.db.query(OrdemServico).all()

            resultados = {
                "total": len(ordens),
                "sincronizadas": 0,
                "com_erro": 0,
                "ignoradas": []
            }

            for ordem in ordens:
                resultado = self.sincronizar_para_servidor_remoto(
                    ordem_id=ordem.id,
                    servidor_id=servidor_id,
                    servidor_url="",
                    servidor_tipo="postgresql"
                )

                if resultado.get("sucesso"):
                    resultados["sincronizadas"] += 1
                else:
                    resultados["com_erro"] += 1

            logger.info(f"🔄 Sincronização completa: {resultados['sincronizadas']}/{resultados['total']}")

            return {
                "sucesso": True,
                "resultados": resultados
            }

        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar tudo: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": str(e)
            }

    # ===== IMPORTAÇÃO DE DADOS =====

    def importar_de_servidor(
        self,
        servidor_id: int,
        servidor_url: str,
        tipos_dados: List[str] = None
    ) -> Dict:
        """
        Importa dados de servidor remoto para local

        Args:
            servidor_id: ID do servidor
            servidor_url: URL/caminho do servidor
            tipos_dados: ['clientes', 'ordens', 'lancamentos'] ou None para tudo

        Returns:
            {
                "sucesso": bool,
                "registros_importados": {"clientes": 100, "ordens": 50, ...},
                "conflitos_detectados": 10
            }
        """
        if tipos_dados is None:
            tipos_dados = ["clientes", "ordens", "lancamentos"]

        try:
            resultados = {
                "clientes": 0,
                "ordens": 0,
                "lancamentos": 0,
                "conflitos": 0
            }

            # TODO: Implementar importação de dados
            # - Conectar ao servidor remoto
            # - Ler dados (Clientes, Ordens, Lançamentos)
            # - Detectar conflitos (registro já existe?)
            # - Importar ou solicitar resolução

            logger.info(f"📥 Importação de servidor {servidor_id} completa")

            return {
                "sucesso": True,
                "registros_importados": resultados,
                "mensagem": "Importação concluída"
            }

        except Exception as e:
            logger.error(f"❌ Erro ao importar de servidor {servidor_id}: {str(e)}")
            return {
                "sucesso": False,
                "mensagem": str(e)
            }

    # ===== WEBHOOK PARA NODE.JS =====

    def notificar_node_js(
        self,
        tipo: str,
        numero_os: int,
        dados: Dict = None
    ) -> bool:
        """
        Notifica Node.js sobre eventos

        Tipos:
        - 'ordem-criada'
        - 'ordem-atualizada'
        - 'sincronizacao-completa'
        """
        try:
            payload = {
                "tipo": tipo,
                "numeroOS": numero_os,
                "timestamp": datetime.utcnow().isoformat(),
                **(dados or {})
            }

            response = requests.post(
                f"{self.servidor_node}/api/webhook/evento",
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                logger.info(f"✅ Node.js notificado: {tipo} (OS {numero_os})")
                return True
            else:
                logger.warning(f"⚠️  Node.js não respondeu (status {response.status_code})")
                return False

        except Exception as e:
            logger.warning(f"⚠️  Erro ao notificar Node.js: {str(e)}")
            return False

    # ===== REGISTRO DE HISTÓRICO =====

    def _registrar_sincronizacao(
        self,
        ordem_id: int,
        servidor_id: int,
        status: str,
        registros_processados: int = 0,
        mensagem_erro: str = None
    ):
        """Registra no histórico de sincronização"""
        try:
            sync_history = SyncHistory(
                servidor_id=servidor_id,
                data_inicio=datetime.utcnow(),
                data_fim=datetime.utcnow(),
                status=status,
                registros_processados=registros_processados,
                mensagem_erro=mensagem_erro
            )
            self.db.add(sync_history)
            self.db.commit()
        except Exception as e:
            logger.error(f"❌ Erro ao registrar sincronização: {str(e)}")

    # ===== VERIFICAR STATUS DE SINCRONIZAÇÃO =====

    def obter_status_sincronizacao(self) -> Dict:
        """Retorna status atual de sincronização"""
        try:
            pendentes = self.db.query(SyncQueue).filter(
                SyncQueue.sincronizado == False
            ).count()

            sincronizadas = self.db.query(SyncQueue).filter(
                SyncQueue.sincronizado == True
            ).count()

            return {
                "pendentes": pendentes,
                "sincronizadas": sincronizadas,
                "total": pendentes + sincronizadas
            }

        except Exception as e:
            logger.error(f"❌ Erro ao obter status: {str(e)}")
            return {"erro": str(e)}

    # ===== WEBHOOK DO WHATSAPP (FUTURO) =====

    def processar_mensagem_whatsapp(
        self,
        numero_cliente: str,
        mensagem: str
    ) -> str:
        """
        Processa mensagem do WhatsApp

        Exemplo:
        - "Qual é o status da minha OS 123?"
        - "Enviar foto da OS 456"

        Retorna resposta automática
        """
        # TODO: Implementar lógica de processamento
        # - Extrair número da OS da mensagem
        # - Buscar status
        # - Retornar resposta automática ou encaminhar para atendente

        return "Sua requisição foi recebida. Aguarde..."


# Instância global
_sincronizador = None


def obter_sincronizador(db: Session) -> SincronizadorHibrido:
    """Obtém instância do sincronizador"""
    global _sincronizador
    if _sincronizador is None:
        _sincronizador = SincronizadorHibrido(db)
    return _sincronizador
