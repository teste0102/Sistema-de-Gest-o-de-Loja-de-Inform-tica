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
    telefone_contato_2 = Column(String(20))  # segundo telefone (opcional)
    observacao = Column(Text)                 # observação do cliente/atendimento

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

class Produto(Base):
    """Tabela de Produtos / Estoque (importado de ESTO.MDB do programa antigo)"""
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_barras = Column(String(30), index=True)   # ESTO.CODIGO (código de barras)
    descricao = Column(String(255), nullable=False, index=True)  # ESTO.E5
    unidade = Column(String(20))                      # ESTO.E6 (CX/UN/PC/CONJ)
    marca = Column(String(80), index=True)            # ESTO.E7
    preco_custo = Column(Float, default=0.0)          # ESTO.E8
    preco_venda = Column(Float, default=0.0)          # ESTO.E22
    estoque = Column(Float, default=0.0)              # ESTO.E30 (quantidade)
    categoria = Column(String(80), index=True)        # ESTO.S2
    status = Column(String(20), default="ATIVO")      # ESTO.ST
    ncm = Column(String(20))                          # ESTO.T2 (fiscal)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    itens_venda = relationship("VendaItem", back_populates="produto")

class MovimentoEstoque(Base):
    """
    Movimento de estoque (event-sourcing). O estoque de um produto é a SOMA dos
    deltas de seus movimentos. Cada movimento tem um uid GLOBAL único para
    sincronizar entre terminais sem duplicar nem sobrescrever contagens.
      - eventos (venda/ajuste/entrada): uid = "<terminal>:<hex>", append-only.
      - baseline (contagem inicial/importação): uid = "base:<codigo_barras>", upsert.
    """
    __tablename__ = "movimentos_estoque"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(80), unique=True, index=True)
    codigo_barras = Column(String(30), index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=True)
    tipo = Column(String(15))          # inicial, entrada, saida, ajuste
    quantidade = Column(Float, default=0.0)  # magnitude informada
    delta = Column(Float, default=0.0)       # efeito no estoque (assinado)
    origem = Column(String(30))        # importacao, venda, manual, backfill
    referencia = Column(String(40))    # ex.: código da venda
    terminal_id = Column(String(40))
    observacao = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Venda(Base):
    """Tabela de Vendas (cabeçalho) - importado de VENDAS.MDB / tabela CADA"""
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), index=True)           # CADA.CODIGO (número da venda)
    vendedor = Column(String(120))                    # CADA.VENDEDOR
    cliente_nome = Column(String(120))                # CADA.CLIENTE
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    pagamento = Column(String(40))                    # CADA.PAGAMENTO (A VISTA)
    desconto = Column(Float, default=0.0)             # CADA.DES
    valor_total = Column(Float, default=0.0)          # CADA.VALOR
    data = Column(Date, index=True)                   # CADA.DATA
    hora = Column(String(10))                         # CADA.HORA
    origem = Column(String(20), default="novo")       # novo | importado
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    itens = relationship("VendaItem", back_populates="venda", cascade="all, delete-orphan")

class VendaItem(Base):
    """Itens (linhas) de cada venda"""
    __tablename__ = "venda_itens"

    id = Column(Integer, primary_key=True, index=True)
    venda_id = Column(Integer, ForeignKey("vendas.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=True)
    codigo_produto = Column(String(30))               # CADA.COD
    descricao = Column(String(255))                   # CADA.PRODUTO
    unidade = Column(String(20))                      # CADA.UNIDADE
    quantidade = Column(Float, default=1.0)           # CADA.QTDA
    preco_unitario = Column(Float, default=0.0)       # CADA.VENDA
    subtotal = Column(Float, default=0.0)             # CADA.SUB
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    venda = relationship("Venda", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_venda")

class SyncConfig(Base):
    """Configuração da sincronização automática entre terminais (linha única)."""
    __tablename__ = "sync_config"

    id = Column(Integer, primary_key=True, index=True)
    terminal_id = Column(String(40))          # identifica este terminal (ex.: terminal-a1b2)
    modo = Column(String(10), default="pasta")  # pasta | ssh
    # Modo pasta (rede/local montada no container)
    pasta_local = Column(String(255))         # caminho da pasta compartilhada
    # Modo SSH (outro PC)
    ssh_host = Column(String(120))
    ssh_porta = Column(Integer, default=22)
    ssh_usuario = Column(String(80))
    ssh_senha = Column(String(120))
    ssh_caminho = Column(String(255), default=".")
    # Agendamento
    intervalo_min = Column(Integer, default=5)
    ativo = Column(Boolean, default=False)
    ultima_sync = Column(DateTime)
    ultimo_status = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
