"""
models.py - Modelos SQLAlchemy (ORM)
Define as tabelas do banco de dados
"""

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, ForeignKey, Boolean, JSON, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Cliente(Base):
    """Tabela de clientes (de CADA.MDB)"""
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(Integer, unique=True, index=True)
    nome = Column(String(120), nullable=False, index=True)
    endereco = Column(String(150))
    cidade = Column(String(80))
    cep = Column(String(10))
    telefone = Column(String(15))
    email = Column(String(120))
    contato = Column(String(60))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    ordens = relationship("OrdemServico", back_populates="cliente", cascade="all, delete-orphan")
    lancamentos = relationship("Lancamento", back_populates="cliente", cascade="all, delete-orphan")

class OrdemServico(Base):
    """Tabela de Ordens de Serviço (de OS.MDB)"""
    __tablename__ = "ordens_servico"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, unique=True, index=True)
    numero_os = Column(String(20), unique=True, index=True)  # Formato: OS-YYYYMMDD-XXXXX
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    descricao = Column(Text)
    data_abertura = Column(Date, index=True)
    data_criacao = Column(DateTime, default=datetime.utcnow, index=True)
    data_fechamento = Column(Date)
    status = Column(String(20), default="aberto")  # aberto, fechado, suspenso, aberta
    tecnico = Column(String(60))
    observacoes = Column(Text)
    valor_total = Column(Float, default=0.0)

    # NOVOS CAMPOS - Integração com Atendimento (Node.js)
    node_os_id = Column(String(50))  # ID da OS no Node.js
    node_senha_id = Column(String(50))  # ID da senha no Node.js

    # Dispositivo - FUNDAMENTAL
    marca = Column(String(60), index=True)  # Samsung, Apple, Xiaomi, Motorola, ASUS, etc.
    modelo = Column(String(120), index=True)  # Galaxy S10, iPhone 12, etc.
    imei = Column(String(20), unique=True, nullable=True, index=True)  # IMEI do dispositivo

    # Produto (assistente de cadastro)
    produto_tipo = Column(String(30))  # celular, pc, pc_gamer, outro
    produto_descricao = Column(String(255))  # descrição livre quando tipo = outro

    # Endereço / Contato (assistente de cadastro)
    nome_cliente = Column(String(120))  # nome do cliente digitado na OS
    endereco_rua = Column(String(150))
    endereco_tipo = Column(String(20))  # casa, ap
    endereco_complemento = Column(String(120))
    endereco_numero = Column(String(20))
    bairro = Column(String(80))
    cidade_os = Column(String(80))
    telefone_contato = Column(String(20))

    # Problema relatado
    problema_descricao = Column(Text)

    # Orçamento (valores estimados + parcelamento)
    valor_aprovado_estimado = Column(Float, default=0.0)   # valor aprovado de referência
    valor_aprovado_parcelas = Column(Integer, default=1)   # em quantas vezes
    valor_total_estimado = Column(Float, default=0.0)      # valor total estimado
    valor_total_parcelas = Column(Integer, default=1)      # em quantas vezes

    # Assinatura digital do cliente (caneta USB) - imagem base64 PNG
    assinatura_cliente = Column(Text)

    # Senhas
    senha_tipo = Column(String(20))  # pin, padrao, biometria, nenhuma
    senha_imagem = Column(Text)  # imagem do padrão (base64)
    senha_cifrada = Column(String(255))  # senha criptografada

    # Replay de digitação (sequência de toques)
    replay_dados = Column(Text)  # JSON com sequência de toques {sequencia, duracao_ms, dispositivo, data_criacao}

    # Mídias
    fotos = Column(JSON)  # [{id, url, data, descricao}, ...]
    videos = Column(JSON)  # [{id, url, duracao, data}, ...]

    # Laudo Técnico (relatório final)
    laudo_assinatura_digital = Column(Text)  # Assinatura RSA-2048 do técnico
    laudo_chave_publica = Column(Text)  # Chave pública RSA para validar a assinatura
    laudo_payload_assinado = Column(Text)  # Payload exato que foi assinado (para validação)
    laudo_danos = Column(JSON)  # [{tipo, descricao, foto_ids}, ...]
    laudo_data_criacao = Column(DateTime)  # Quando o laudo foi criado
    laudo_assinado_cliente = Column(Boolean, default=False)  # Assinatura do cliente com caneta USB

    # Rastreamento de sincronização
    sincronizado_com_servidores = Column(JSON, default={})  # {servidor_id: timestamp}
    apenas_novo_servidor = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="ordens")
    itens = relationship("OrdemItem", back_populates="ordem", cascade="all, delete-orphan")
    lancamentos = relationship("Lancamento", back_populates="ordem", cascade="all, delete-orphan")

class OrdemItem(Base):
    """Itens de cada Ordem de Serviço"""
    __tablename__ = "ordem_itens"
    
    id = Column(Integer, primary_key=True, index=True)
    ordem_id = Column(Integer, ForeignKey("ordens_servico.id"), nullable=False)
    descricao = Column(String(255), nullable=False)
    quantidade = Column(Float, default=1.0)
    valor_unitario = Column(Float, default=0.0)
    valor_total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamento
    ordem = relationship("OrdemServico", back_populates="itens")

class Lancamento(Base):
    """Tabela de Financeiro (de CAIXA.MDB)"""
    __tablename__ = "lancamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, nullable=False, index=True)
    tipo = Column(String(10), nullable=False)  # receita, despesa
    categoria = Column(String(60), index=True)
    descricao = Column(String(255))
    valor = Column(Float, nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    ordem_id = Column(Integer, ForeignKey("ordens_servico.id"))
    forma_pagamento = Column(String(30))  # dinheiro, cartao, cheque, transferencia
    numero_recibo = Column(String(20))
    baixado = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="lancamentos")
    ordem = relationship("OrdemServico", back_populates="lancamentos")

class SyncQueue(Base):
    """Fila de sincronização para offline-first"""
    __tablename__ = "sync_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    tabela = Column(String(50), nullable=False)
    operacao = Column(String(10), nullable=False)  # insert, update, delete
    registro_id = Column(Integer)
    dados = Column(JSON)  # Dados completos da operação
    timestamp = Column(DateTime, default=datetime.utcnow)
    sincronizado = Column(Boolean, default=False)
    erro = Column(Text)

class ServidorRemoto(Base):
    """Servidores remotos para sincronização multi-servidor"""
    __tablename__ = "servidores_remotos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    url = Column(String(255), nullable=False)
    chave_api = Column(String(255))
    ativo = Column(Boolean, default=True)
    ultima_sincronizacao = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Usuario(Base):
    """Usuários do sistema (login)"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(60), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    nome = Column(String(120))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    """Log de auditoria de todas operações"""
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    tabela = Column(String(50), nullable=False)
    operacao = Column(String(10), nullable=False)  # insert, update, delete
    registro_id = Column(Integer)
    usuario = Column(String(60))
    dados_antigos = Column(JSON)
    dados_novos = Column(JSON)
    ip_address = Column(String(15))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
