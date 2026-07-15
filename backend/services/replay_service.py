"""
Serviço de Replay de Digitação
Captura e reproduz a sequência de toques do usuário
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
import json

from models import OrdemServico
from utils.crypto_service import CryptoService


class ReplayDigitacaoDTO:
    """Data Transfer Object para Replay"""
    def __init__(self, ordem_id: int, sequencia: List[Dict], duracao_ms: int, dispositivo: Dict):
        self.ordem_id = ordem_id
        self.sequencia = sequencia
        self.duracao_ms = duracao_ms
        self.dispositivo = dispositivo
        self.data_criacao = datetime.now()


class ReplayService:
    """Serviço para gerenciar replay de digitação"""

    @staticmethod
    def registrar_replay(
        db: Session,
        ordem_id: int,
        sequencia: List[Dict],
        duracao_ms: int,
        dispositivo: Dict
    ) -> Dict:
        """
        Registra sequência de toques (replay de digitação)

        Formato de sequência:
        [
            {"x": 100, "y": 200, "t": 0, "tipo": "toque", "forca": 0.8},
            {"x": 150, "y": 250, "t": 100, "tipo": "toque", "forca": 0.9},
            {"x": 200, "y": 200, "t": 200, "tipo": "movimento", "forca": 0.7},
            {"x": 150, "y": 250, "t": 300, "tipo": "levanta"}
        ]

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem
            sequencia: Lista de eventos de toque
            duracao_ms: Duração total em milissegundos
            dispositivo: Info do dispositivo (modelo, SO, resolução)

        Returns:
            Dict com resultado da operação
        """
        try:
            # Validar sequência
            if not sequencia or not isinstance(sequencia, list):
                raise ValueError("Sequência deve ser uma lista não vazia")

            if duracao_ms <= 0:
                raise ValueError("Duração deve ser positiva")

            # Validar cada evento
            for evento in sequencia:
                if not isinstance(evento, dict):
                    raise ValueError("Cada evento deve ser um dicionário")
                if "x" not in evento or "y" not in evento or "t" not in evento:
                    raise ValueError("Cada evento deve ter x, y e t (tempo)")

            # Obter ordem
            ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
            if not ordem:
                raise ValueError(f"Ordem {ordem_id} não encontrada")

            # Armazenar replay como JSON
            replay_data = {
                "sequencia": sequencia,
                "duracao_ms": duracao_ms,
                "dispositivo": dispositivo,
                "data_criacao": datetime.now().isoformat(),
                "num_eventos": len(sequencia)
            }

            ordem.replay_dados = json.dumps(replay_data)
            db.add(ordem)
            db.commit()

            return {
                "ok": True,
                "ordem_id": ordem_id,
                "num_eventos": len(sequencia),
                "duracao_ms": duracao_ms,
                "mensagem": "Replay registrado com sucesso"
            }

        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao registrar replay: {str(e)}")

    @staticmethod
    def obter_replay(db: Session, ordem_id: int) -> Optional[Dict]:
        """
        Obtém replay armazenado

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem

        Returns:
            Dict com replay ou None
        """
        try:
            ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
            if not ordem or not ordem.replay_dados:
                return None

            # Desserializar JSON
            replay_data = json.loads(ordem.replay_dados)
            return replay_data

        except Exception:
            return None

    @staticmethod
    def calcular_estatisticas_replay(sequencia: List[Dict]) -> Dict:
        """
        Calcula estatísticas do replay

        Args:
            sequencia: Lista de eventos de toque

        Returns:
            Dict com estatísticas
        """
        try:
            if not sequencia:
                return {}

            # Distância total percorrida
            distancia_total = 0.0
            velocidade_media = 0.0

            for i in range(len(sequencia) - 1):
                evento_atual = sequencia[i]
                evento_proximo = sequencia[i + 1]

                x1, y1 = evento_atual.get("x", 0), evento_atual.get("y", 0)
                x2, y2 = evento_proximo.get("x", 0), evento_proximo.get("y", 0)
                t1, t2 = evento_atual.get("t", 0), evento_proximo.get("t", 0)

                # Distância euclidiana
                dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                distancia_total += dist

                # Velocidade
                if t2 > t1:
                    velocidade_media += dist / (t2 - t1)

            # Número de toques
            num_toques = sum(1 for e in sequencia if e.get("tipo") == "toque")

            # Tempo de pausa total
            tempo_pausa = 0
            tempos = [e.get("t", 0) for e in sequencia]
            for i in range(len(tempos) - 1):
                if tempos[i + 1] - tempos[i] > 200:  # Mais de 200ms é pausa
                    tempo_pausa += tempos[i + 1] - tempos[i]

            return {
                "distancia_total": round(distancia_total, 2),
                "velocidade_media": round(velocidade_media / len(sequencia), 2) if sequencia else 0,
                "num_toques": num_toques,
                "tempo_pausa_ms": tempo_pausa,
                "num_eventos": len(sequencia)
            }

        except Exception:
            return {}

    @staticmethod
    def validar_replay(sequencia: List[Dict]) -> Tuple[bool, str]:
        """
        Valida integridade de um replay

        Args:
            sequencia: Sequência de eventos

        Returns:
            Tupla (válido, mensagem)
        """
        if not sequencia:
            return False, "Sequência vazia"

        if not isinstance(sequencia, list):
            return False, "Sequência deve ser lista"

        # Validar campos obrigatórios
        for i, evento in enumerate(sequencia):
            if not isinstance(evento, dict):
                return False, f"Evento {i} não é dicionário"

            if "x" not in evento or "y" not in evento or "t" not in evento:
                return False, f"Evento {i} missing required fields (x, y, t)"

            if not isinstance(evento["x"], (int, float)):
                return False, f"Evento {i}: x deve ser número"

            if not isinstance(evento["y"], (int, float)):
                return False, f"Evento {i}: y deve ser número"

            if not isinstance(evento["t"], (int, float)):
                return False, f"Evento {i}: t deve ser número"

            if evento["t"] < 0:
                return False, f"Evento {i}: tempo não pode ser negativo"

        # Validar sequência temporal
        tempos_anteriores = []
        for i, evento in enumerate(sequencia):
            tempo = evento.get("t", 0)
            if tempos_anteriores and tempo < tempos_anteriores[-1]:
                return False, f"Evento {i}: tempo não está em ordem crescente"
            tempos_anteriores.append(tempo)

        return True, "Replay válido"

    @staticmethod
    def deletar_replay(db: Session, ordem_id: int) -> Dict:
        """
        Deleta replay armazenado

        Args:
            db: Sessão de banco de dados
            ordem_id: ID da ordem

        Returns:
            Dict com resultado
        """
        try:
            ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
            if not ordem:
                raise ValueError(f"Ordem {ordem_id} não encontrada")

            if not ordem.replay_dados:
                raise ValueError("Nenhum replay para deletar")

            ordem.replay_dados = None
            db.add(ordem)
            db.commit()

            return {
                "ok": True,
                "mensagem": "Replay deletado com sucesso"
            }

        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao deletar replay: {str(e)}")

    @staticmethod
    def gerar_uuid_replay() -> str:
        """Gera UUID para replay"""
        return CryptoService.gerar_uuid_replay()


# ============================================================================
# TESTES RÁPIDOS
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE REPLAY DE DIGITAÇÃO")
    print("=" * 60)

    # Teste de sequência válida
    sequencia_teste = [
        {"x": 100, "y": 200, "t": 0, "tipo": "toque"},
        {"x": 150, "y": 250, "t": 100, "tipo": "movimento"},
        {"x": 200, "y": 200, "t": 200, "tipo": "toque"},
        {"x": 150, "y": 150, "t": 300, "tipo": "levanta"}
    ]

    print("\n1. VALIDAÇÃO DE REPLAY")
    valido, msg = ReplayService.validar_replay(sequencia_teste)
    print(f"  Válido: {valido}")
    print(f"  Mensagem: {msg}")

    print("\n2. ESTATÍSTICAS")
    stats = ReplayService.calcular_estatisticas_replay(sequencia_teste)
    print(f"  Distância total: {stats.get('distancia_total')} px")
    print(f"  Velocidade média: {stats.get('velocidade_media')} px/ms")
    print(f"  Número de toques: {stats.get('num_toques')}")
    print(f"  Eventos: {stats.get('num_eventos')}")

    # Teste de sequência inválida
    print("\n3. VALIDAÇÃO INVÁLIDA")
    sequencia_invalida = [{"x": 100}]  # Falta y e t
    valido, msg = ReplayService.validar_replay(sequencia_invalida)
    print(f"  Válido: {valido}")
    print(f"  Erro: {msg}")

    print("\n4. UUID")
    print(f"  UUID Replay: {ReplayService.gerar_uuid_replay()}")
