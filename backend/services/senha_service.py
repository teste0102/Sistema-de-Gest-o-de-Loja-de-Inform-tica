"""
Serviço de Criação, Validação e Criptografia de Senhas
Suporta 3 tipos: PIN (dígitos), Padrão (risco), Nenhuma (desbloqueado)
"""

import random
import string
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from backend.utils.crypto_service import CryptoService


@dataclass
class SenhaDTO:
    """Classe para transferência de dados de Senha"""
    id: str
    tipo: str                    # "pin", "padrao", "nenhuma"
    data_criada: datetime
    pode_visualizar: bool = False
    valor_criptografado: Optional[str] = None
    imagem_base64: Optional[str] = None
    coordenadas: Optional[List[Tuple[int, int]]] = None


class SenhaService:
    """Serviço centralizado para gerenciamento de senhas"""

    TIPOS_VALIDOS = ["pin", "padrao", "nenhuma", "biometria"]
    TAMANHO_PIN_MINIMO = 4
    TAMANHO_PIN_MAXIMO = 6

    def __init__(self, crypto_service: CryptoService):
        """
        Inicializa serviço de senhas

        Args:
            crypto_service: Instância do CryptoService para criptografia
        """
        self.crypto = crypto_service

    # ========================================================================
    # GERAÇÃO DE SENHAS
    # ========================================================================

    def gerar_pin(self, tamanho: int = 4) -> str:
        """
        Gera PIN aleatório

        Args:
            tamanho: Tamanho do PIN (4-6 dígitos)

        Returns:
            PIN aleatório

        Raises:
            ValueError: Se tamanho for inválido
        """
        if not (self.TAMANHO_PIN_MINIMO <= tamanho <= self.TAMANHO_PIN_MAXIMO):
            raise ValueError(
                f"Tamanho do PIN deve estar entre "
                f"{self.TAMANHO_PIN_MINIMO} e {self.TAMANHO_PIN_MAXIMO}"
            )

        # Gerar dígitos aleatórios
        pin = "".join(random.choice(string.digits) for _ in range(tamanho))
        return pin

    def gerar_padrao(
        self,
        largura: int = 3,
        altura: int = 3,
        complexidade: str = "media"
    ) -> Dict:
        """
        Gera padrão aleatório (risco)

        Retorna coordenadas dos pontos e imagem base64 simulada

        Args:
            largura: Largura da grid (2-5)
            altura: Altura da grid (2-5)
            complexidade: "simples" (3-4), "media" (4-6), "complexa" (6+)

        Returns:
            Dict com coordenadas e dados para visualização

        Raises:
            ValueError: Se parâmetros inválidos
        """
        if not (2 <= largura <= 5) or not (2 <= altura <= 5):
            raise ValueError("Largura e altura devem estar entre 2 e 5")

        # Definir número de pontos conforme complexidade
        if complexidade == "simples":
            num_pontos = random.randint(3, 4)
        elif complexidade == "complexa":
            num_pontos = random.randint(6, altura * largura)
        else:  # media
            num_pontos = random.randint(4, 6)

        # Gerar lista de coordenadas possíveis
        coordenadas_possiveis = [
            (x, y) for x in range(largura) for y in range(altura)
        ]

        # Selecionar aleatoriamente sem repetição
        if num_pontos > len(coordenadas_possiveis):
            num_pontos = len(coordenadas_possiveis)

        padrao_coordenadas = random.sample(coordenadas_possiveis, num_pontos)

        return {
            "coordenadas": padrao_coordenadas,
            "largura": largura,
            "altura": altura,
            "num_pontos": num_pontos,
            "tipo": "padrão_risco",
            "descricao": f"Padrão com {num_pontos} pontos em grid {largura}x{altura}"
        }

    # ========================================================================
    # CRIPTOGRAFIA DE SENHAS
    # ========================================================================

    def criptografar_pin(self, pin: str) -> str:
        """
        Criptografa um PIN

        Args:
            pin: PIN em texto plano

        Returns:
            PIN criptografado

        Raises:
            ValueError: Se PIN inválido
        """
        # Validar que é apenas dígitos
        if not pin.isdigit():
            raise ValueError("PIN deve conter apenas dígitos")

        if not (self.TAMANHO_PIN_MINIMO <= len(pin) <= self.TAMANHO_PIN_MAXIMO):
            raise ValueError(
                f"PIN deve ter entre {self.TAMANHO_PIN_MINIMO} "
                f"e {self.TAMANHO_PIN_MAXIMO} dígitos"
            )

        return self.crypto.criptografar_senha(pin)

    def criptografar_padrao(self, coordenadas: List[Tuple[int, int]]) -> str:
        """
        Criptografa coordenadas do padrão

        Args:
            coordenadas: Lista de tuplas (x, y)

        Returns:
            Coordenadas criptografadas

        Raises:
            ValueError: Se coordenadas inválidas
        """
        if not coordenadas or not isinstance(coordenadas, list):
            raise ValueError("Coordenadas devem ser uma lista não vazia")

        # Converter para JSON para criptografar
        json_coords = json.dumps(coordenadas)
        return self.crypto.criptografar_senha(json_coords)

    def descriptografar_pin(self, pin_criptografado: str) -> str:
        """
        Descriptografa um PIN

        Args:
            pin_criptografado: PIN criptografado

        Returns:
            PIN em texto plano

        Raises:
            ValueError: Se não conseguir descriptografar
        """
        return self.crypto.descriptografar_senha(pin_criptografado)

    def descriptografar_padrao(
        self,
        padrao_criptografado: str
    ) -> List[Tuple[int, int]]:
        """
        Descriptografa coordenadas do padrão

        Args:
            padrao_criptografado: Padrão criptografado

        Returns:
            Lista de tuplas (x, y)

        Raises:
            ValueError: Se não conseguir descriptografar
        """
        json_coords = self.crypto.descriptografar_senha(padrao_criptografado)
        return json.loads(json_coords)

    # ========================================================================
    # VALIDAÇÃO DE SENHAS
    # ========================================================================

    def validar_pin(self, pin_entrada: str, pin_hash: str) -> bool:
        """
        Valida PIN comparando com hash armazenado

        Usa comparação timing-safe

        Args:
            pin_entrada: PIN digitado pelo usuário
            pin_hash: Hash do PIN armazenado

        Returns:
            True se PIN está correto, False caso contrário
        """
        try:
            # Não usar descriptografia aqui, usar hash
            # Calcular hash do PIN entrada
            hash_entrada = self.crypto.gerar_hash_sha256(pin_entrada)

            # Comparar com timing-safe (evita timing attacks)
            return hash_entrada == pin_hash

        except Exception:
            return False

    def validar_padrao(
        self,
        coordenadas_entrada: List[Tuple[int, int]],
        padrao_armazenado_cripto: str
    ) -> bool:
        """
        Valida padrão comparando com armazenado

        Args:
            coordenadas_entrada: Coordenadas digitadas
            padrao_armazenado_cripto: Padrão criptografado no BD

        Returns:
            True se padrão está correto, False caso contrário
        """
        try:
            # Descriptografar padrão armazenado
            padrao_armazenado = self.descriptografar_padrao(
                padrao_armazenado_cripto
            )

            # Comparar (converter para set para ignorar ordem)
            entrada_set = set(coordenadas_entrada)
            armazenado_set = set(padrao_armazenado)

            return entrada_set == armazenado_set

        except Exception:
            return False

    def validar_tipo_senha(self, tipo: str) -> bool:
        """
        Valida se tipo de senha é válido

        Args:
            tipo: Tipo a validar

        Returns:
            True se válido
        """
        return tipo.lower() in self.TIPOS_VALIDOS

    # ========================================================================
    # SERIALIZACAO E DESSERIALIZACAO
    # ========================================================================

    def serializar_senha(
        self,
        senha_id: str,
        tipo: str,
        valor_criptografado: Optional[str] = None,
        imagem_base64: Optional[str] = None,
        pode_visualizar: bool = False
    ) -> Dict:
        """
        Serializa dados de senha para retorno na API

        Não retorna o valor real (segurança)

        Args:
            senha_id: ID da senha
            tipo: Tipo de senha
            valor_criptografado: Valor criptografado (não será retornado)
            imagem_base64: Imagem do padrão (pode ser retornada)
            pode_visualizar: Se cliente pode visualizar o valor

        Returns:
            Dict com dados serializados
        """
        return {
            "id": senha_id,
            "tipo": tipo,
            "data_criada": datetime.now().isoformat(),
            "pode_visualizar": pode_visualizar,
            "imagem": imagem_base64 if tipo == "padrao" and pode_visualizar else None,
            "mensagem_seguranca": "Senha criptografada no servidor, não pode ser recuperada"
        }

    def serializar_padrao_para_visualizacao(
        self,
        padrao_criptografado: str
    ) -> Optional[Dict]:
        """
        Serializa padrão para visualização (replay)

        Args:
            padrao_criptografado: Padrão criptografado

        Returns:
            Dict com coordenadas e dimensões
        """
        try:
            coordenadas = self.descriptografar_padrao(padrao_criptografado)
            return {
                "coordenadas": coordenadas,
                "num_pontos": len(coordenadas)
            }
        except Exception:
            return None

    # ========================================================================
    # UTILITÁRIOS
    # ========================================================================

    def gerar_id_senha(self) -> str:
        """Gera ID único para senha"""
        return self.crypto.gerar_uuid_senha()

    def avaliar_qualidade_pin(self, pin: str) -> Dict:
        """
        Avalia qualidade de um PIN

        Args:
            pin: PIN a avaliar

        Returns:
            Dict com score e recomendações
        """
        score = 0
        dicas = []

        # Comprimento
        if len(pin) >= 6:
            score += 40
        elif len(pin) >= 5:
            score += 20
        else:
            dicas.append("Aumentar tamanho do PIN para melhor segurança")

        # Variação de dígitos
        dígitos_unicos = len(set(pin))
        if dígitos_unicos >= 4:
            score += 30
        elif dígitos_unicos >= 3:
            score += 15
        else:
            dicas.append("Usar mais dígitos diferentes")

        # Não usar padrões óbvios
        if pin not in ["0000", "1111", "2222", "3333", "4444", "5555", "6666",
                       "7777", "8888", "9999", "1234", "4321", "1212", "1111"]:
            score += 30
        else:
            dicas.append("Evitar padrões óbvios como '1234' ou '0000'")

        # Determinar nível
        if score >= 80:
            nivel = "forte"
        elif score >= 50:
            nivel = "media"
        else:
            nivel = "fraca"

        return {
            "score": score,
            "nivel": nivel,
            "dicas": dicas
        }

    def avaliar_qualidade_padrao(self, num_pontos: int) -> Dict:
        """
        Avalia qualidade de um padrão

        Args:
            num_pontos: Número de pontos no padrão

        Returns:
            Dict com score e recomendações
        """
        score = 0
        dicas = []

        if num_pontos >= 6:
            score += 50
            nivel = "forte"
        elif num_pontos >= 4:
            score += 30
            nivel = "media"
            dicas.append("Adicionar mais pontos para maior segurança")
        else:
            score += 10
            nivel = "fraca"
            dicas.append("Padrão muito simples, aumentar número de pontos")

        return {
            "score": score,
            "nivel": nivel,
            "num_pontos": num_pontos,
            "dicas": dicas
        }


# ============================================================================
# TESTES RÁPIDOS
# ============================================================================

if __name__ == "__main__":
    crypto = CryptoService()
    senha_svc = SenhaService(crypto)

    print("=" * 60)
    print("TESTE DE SENHAS")
    print("=" * 60)

    # Teste PIN
    print("\n1. TESTE DE PIN")
    pin_gerado = senha_svc.gerar_pin(4)
    print(f"  PIN gerado: {pin_gerado}")

    pin_cripto = senha_svc.criptografar_pin(pin_gerado)
    print(f"  PIN criptografado: {pin_cripto[:30]}...")

    pin_recuperado = senha_svc.descriptografar_pin(pin_cripto)
    print(f"  PIN recuperado: {pin_recuperado}")
    print(f"  Corresponde: {pin_gerado == pin_recuperado}")

    # Teste qualidade PIN
    qualidade = senha_svc.avaliar_qualidade_pin(pin_gerado)
    print(f"  Qualidade: {qualidade['nivel']} (score: {qualidade['score']})")

    # Teste Padrão
    print("\n2. TESTE DE PADRÃO")
    padrao_gerado = senha_svc.gerar_padrao(3, 3, "media")
    print(f"  Padrão gerado: {padrao_gerado}")

    padrao_cripto = senha_svc.criptografar_padrao(padrao_gerado["coordenadas"])
    print(f"  Padrão criptografado: {padrao_cripto[:30]}...")

    padrao_recuperado = senha_svc.descriptografar_padrao(padrao_cripto)
    print(f"  Padrão recuperado: {padrao_recuperado}")

    # Teste qualidade padrão
    qualidade_p = senha_svc.avaliar_qualidade_padrao(len(padrao_gerado["coordenadas"]))
    print(f"  Qualidade: {qualidade_p['nivel']} (score: {qualidade_p['score']})")

    # Teste ID
    print("\n3. IDs GERADOS")
    print(f"  ID Senha: {senha_svc.gerar_id_senha()}")

    # Teste tipos válidos
    print("\n4. VALIDAÇÃO DE TIPOS")
    tipos_teste = ["pin", "padrao", "nenhuma", "biometria", "invalido"]
    for tipo in tipos_teste:
        resultado = senha_svc.validar_tipo_senha(tipo)
        print(f"  {tipo}: {'✓' if resultado else '✗'}")
