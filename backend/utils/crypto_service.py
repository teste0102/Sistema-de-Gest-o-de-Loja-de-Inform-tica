"""
Serviço de Criptografia para Senhas e Assinaturas Digitais
Responsável por: AES, RSA, Hash, Assinatura Digital
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import hashlib
import base64
import os
from typing import Tuple, Optional
import json


class CryptoService:
    """Serviço centralizado de criptografia"""

    def __init__(self, chave_secreta: Optional[str] = None):
        """
        Inicializa o serviço de criptografia

        Args:
            chave_secreta: Chave Fernet para AES (se None, gera nova)
        """
        if chave_secreta:
            self.cipher = Fernet(chave_secreta.encode())
            self.chave_secreta = chave_secreta
        else:
            chave = Fernet.generate_key()
            self.chave_secreta = chave.decode()
            self.cipher = Fernet(chave)

    # ========================================================================
    # CRIPTOGRAFIA AES (SENHAS)
    # ========================================================================

    def criptografar_senha(self, senha: str) -> str:
        """
        Criptografa uma senha com AES-256

        Args:
            senha: Senha em texto plano

        Returns:
            Senha criptografada em base64
        """
        try:
            senha_criptografada = self.cipher.encrypt(senha.encode())
            return base64.b64encode(senha_criptografada).decode()
        except Exception as e:
            raise ValueError(f"Erro ao criptografar senha: {str(e)}")

    def descriptografar_senha(self, senha_criptografada: str) -> str:
        """
        Descriptografa uma senha

        Args:
            senha_criptografada: Senha criptografada em base64

        Returns:
            Senha em texto plano
        """
        try:
            senha_bytes = base64.b64decode(senha_criptografada.encode())
            senha_plana = self.cipher.decrypt(senha_bytes)
            return senha_plana.decode()
        except Exception as e:
            raise ValueError(f"Erro ao descriptografar senha: {str(e)}")

    def gerar_chave_secreta(self) -> str:
        """
        Gera uma nova chave Fernet para AES

        Returns:
            Chave em base64
        """
        return Fernet.generate_key().decode()

    # ========================================================================
    # HASH (VALIDAÇÃO SEM RECUPERAR)
    # ========================================================================

    def gerar_hash_sha256(self, dados: str) -> str:
        """
        Gera hash SHA-256 de dados

        Args:
            dados: Dados a hashear

        Returns:
            Hash em hexadecimal
        """
        return hashlib.sha256(dados.encode()).hexdigest()

    def gerar_hash_sha512(self, dados: str) -> str:
        """Gera hash SHA-512 (mais seguro)"""
        return hashlib.sha512(dados.encode()).hexdigest()

    def gerar_hash_json(self, dados: dict) -> str:
        """
        Gera hash de um dicionário JSON

        Args:
            dados: Dicionário a hashear

        Returns:
            Hash SHA-256
        """
        json_str = json.dumps(dados, sort_keys=True, separators=(',', ':'))
        return self.gerar_hash_sha256(json_str)

    def verificar_hash(self, dados: str, hash_armazenado: str) -> bool:
        """
        Verifica se dados correspondem a um hash

        Args:
            dados: Dados a verificar
            hash_armazenado: Hash para comparar

        Returns:
            True se corresponde, False caso contrário
        """
        hash_calculado = self.gerar_hash_sha256(dados)
        # Usar comparação timing-safe
        return hash_calculado == hash_armazenado

    # ========================================================================
    # ASSINATURA DIGITAL (RSA-2048)
    # ========================================================================

    @staticmethod
    def gerar_par_chaves_rsa(tamanho_bits: int = 2048) -> Tuple[bytes, bytes]:
        """
        Gera par de chaves RSA para assinaturas digitais

        Args:
            tamanho_bits: Tamanho da chave (2048 ou 4096)

        Returns:
            Tupla (chave_privada, chave_publica) em PEM
        """
        chave_privada = rsa.generate_private_key(
            public_exponent=65537,
            key_size=tamanho_bits,
            backend=default_backend()
        )
        chave_publica = chave_privada.public_key()

        # Converter para PEM
        privada_pem = chave_privada.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        publica_pem = chave_publica.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return privada_pem, publica_pem

    def assinar_dados(self, dados: dict, chave_privada_pem: bytes) -> str:
        """
        Assina dados com chave privada RSA

        Args:
            dados: Dicionário a assinar
            chave_privada_pem: Chave privada em PEM

        Returns:
            Assinatura em base64
        """
        try:
            # Converter dict para JSON determinístico
            json_str = json.dumps(dados, sort_keys=True, separators=(',', ':'))
            dados_bytes = json_str.encode()

            # Carregar chave privada
            chave_privada = serialization.load_pem_private_key(
                chave_privada_pem,
                password=None,
                backend=default_backend()
            )

            # Assinar
            assinatura = chave_privada.sign(
                dados_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            # Retornar em base64
            return base64.b64encode(assinatura).decode()

        except Exception as e:
            raise ValueError(f"Erro ao assinar dados: {str(e)}")

    def validar_assinatura(
        self,
        dados: dict,
        assinatura_base64: str,
        chave_publica_pem: bytes
    ) -> bool:
        """
        Valida assinatura digital de dados

        Args:
            dados: Dicionário original
            assinatura_base64: Assinatura em base64
            chave_publica_pem: Chave pública em PEM

        Returns:
            True se válida, False caso contrário
        """
        try:
            # Converter dict para JSON determinístico
            json_str = json.dumps(dados, sort_keys=True, separators=(',', ':'))
            dados_bytes = json_str.encode()

            # Carregar chave pública
            chave_publica = serialization.load_pem_public_key(
                chave_publica_pem,
                backend=default_backend()
            )

            # Decodificar assinatura
            assinatura = base64.b64decode(assinatura_base64.encode())

            # Validar
            chave_publica.verify(
                assinatura,
                dados_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return True

        except Exception as e:
            # Assinatura inválida
            return False

    # ========================================================================
    # UTILITÁRIOS
    # ========================================================================

    @staticmethod
    def gerar_token_aleatorio(tamanho_bytes: int = 32) -> str:
        """
        Gera token aleatório seguro

        Args:
            tamanho_bytes: Tamanho em bytes

        Returns:
            Token em hexadecimal
        """
        return os.urandom(tamanho_bytes).hex()

    @staticmethod
    def gerar_uuid_senha() -> str:
        """Gera UUID para ID de senha"""
        import uuid
        return f"pwd-{uuid.uuid4().hex[:12]}"

    @staticmethod
    def gerar_uuid_foto() -> str:
        """Gera UUID para ID de foto"""
        import uuid
        return f"foto-{uuid.uuid4().hex[:12]}"

    @staticmethod
    def gerar_uuid_replay() -> str:
        """Gera UUID para ID de replay"""
        import uuid
        return f"replay-{uuid.uuid4().hex[:12]}"

    # ========================================================================
    # VALIDAÇÃO DE FORÇA DE SENHA
    # ========================================================================

    @staticmethod
    def avaliar_forca_senha(senha: str) -> dict:
        """
        Avalia a força de uma senha

        Args:
            senha: Senha a avaliar

        Returns:
            Dict com: score (0-100), nivel (fraca/media/forte/muito_forte), dicas
        """
        score = 0
        dicas = []

        # Comprimento
        if len(senha) >= 8:
            score += 20
        else:
            dicas.append("Mínimo 8 caracteres")

        if len(senha) >= 12:
            score += 10

        if len(senha) >= 16:
            score += 10

        # Maiúsculas
        if any(c.isupper() for c in senha):
            score += 15
        else:
            dicas.append("Adicione letras maiúsculas")

        # Minúsculas
        if any(c.islower() for c in senha):
            score += 15
        else:
            dicas.append("Adicione letras minúsculas")

        # Números
        if any(c.isdigit() for c in senha):
            score += 15
        else:
            dicas.append("Adicione números")

        # Caracteres especiais
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in senha):
            score += 15
        else:
            dicas.append("Adicione caracteres especiais")

        # Determinar nível
        if score >= 80:
            nivel = "muito_forte"
        elif score >= 60:
            nivel = "forte"
        elif score >= 40:
            nivel = "media"
        else:
            nivel = "fraca"

        return {
            "score": min(score, 100),
            "nivel": nivel,
            "dicas": dicas
        }


# ============================================================================
# TESTES RÁPIDOS
# ============================================================================

if __name__ == "__main__":
    # Teste básico
    crypto = CryptoService()

    # Teste AES
    print("=" * 60)
    print("TESTE DE CRIPTOGRAFIA AES")
    print("=" * 60)
    senha_original = "MinhaSenha123!@#"
    senha_cripto = crypto.criptografar_senha(senha_original)
    print(f"Original: {senha_original}")
    print(f"Criptografada: {senha_cripto}")
    senha_recuperada = crypto.descriptografar_senha(senha_cripto)
    print(f"Recuperada: {senha_recuperada}")
    print(f"Corresponde: {senha_original == senha_recuperada}\n")

    # Teste Hash
    print("=" * 60)
    print("TESTE DE HASH SHA-256")
    print("=" * 60)
    dados = "Dados importantes"
    hash_dados = crypto.gerar_hash_sha256(dados)
    print(f"Dados: {dados}")
    print(f"Hash: {hash_dados}")
    print(f"Verificação: {crypto.verificar_hash(dados, hash_dados)}\n")

    # Teste RSA
    print("=" * 60)
    print("TESTE DE ASSINATURA DIGITAL RSA")
    print("=" * 60)
    privada, publica = CryptoService.gerar_par_chaves_rsa()
    print(f"Chave privada gerada ({len(privada)} bytes)")
    print(f"Chave pública gerada ({len(publica)} bytes)")

    dados_dict = {"laudo_id": 1, "valor": 500.00}
    assinatura = crypto.assinar_dados(dados_dict, privada)
    print(f"Dados: {dados_dict}")
    print(f"Assinatura: {assinatura[:50]}...")
    valida = crypto.validar_assinatura(dados_dict, assinatura, publica)
    print(f"Assinatura válida: {valida}\n")

    # Teste força de senha
    print("=" * 60)
    print("TESTE DE FORÇA DE SENHA")
    print("=" * 60)
    senhas_teste = [
        "123456",
        "senha",
        "Senha123",
        "Senha123!@#Muito"
    ]
    for s in senhas_teste:
        resultado = CryptoService.avaliar_forca_senha(s)
        print(f"Senha: {s}")
        print(f"  Score: {resultado['score']}/100")
        print(f"  Nível: {resultado['nivel']}")
        print(f"  Dicas: {resultado['dicas']}\n")
