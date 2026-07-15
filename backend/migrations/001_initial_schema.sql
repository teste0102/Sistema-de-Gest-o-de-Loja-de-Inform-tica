-- ============================================================================
-- MIGRATION 001: INITIAL SCHEMA
-- Cria todas as tabelas principais do sistema
-- ============================================================================

-- Criar extensão UUID se não existir
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABELA: clientes
-- ============================================================================
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    telefone VARCHAR(20),
    cpf_cnpj VARCHAR(20) UNIQUE,
    endereco TEXT,
    cidade VARCHAR(100),
    estado VARCHAR(2),
    cep VARCHAR(10),
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABELA: ordens_servico
-- Ordem de Serviço com informações de senha, laudo, replay
-- ============================================================================
CREATE TABLE IF NOT EXISTS ordens_servico (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    numero_os VARCHAR(30) UNIQUE NOT NULL,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    imei VARCHAR(20),
    status VARCHAR(20) DEFAULT 'aberta',

    -- Senha (PIN, Padrão ou Nenhuma)
    node_senha_id VARCHAR(50),
    senha_tipo VARCHAR(20),
    senha_cifrada TEXT,
    senha_imagem TEXT,

    -- Laudo Técnico
    laudo_assinatura_digital TEXT,
    laudo_dados TEXT,

    -- Replay de Digitação
    replay_dados TEXT,

    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABELA: fotos
-- Armazenamento de metadados de fotos
-- ============================================================================
CREATE TABLE IF NOT EXISTS fotos (
    id VARCHAR(50) PRIMARY KEY,
    ordem_id INTEGER NOT NULL REFERENCES ordens_servico(id) ON DELETE CASCADE,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    arquivo VARCHAR(500) NOT NULL,
    thumbnail VARCHAR(500),
    mime_type VARCHAR(50),
    hash_arquivo VARCHAR(100) UNIQUE,
    tamanho INTEGER,
    descricao TEXT,
    tipo_dano VARCHAR(50),
    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABELA: lancamentos (financeiro)
-- ============================================================================
CREATE TABLE IF NOT EXISTS lancamentos (
    id SERIAL PRIMARY KEY,
    ordem_id INTEGER REFERENCES ordens_servico(id) ON DELETE CASCADE,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    tipo VARCHAR(20),
    descricao TEXT,
    valor DECIMAL(10, 2),
    data_lancamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pendente'
);

-- ============================================================================
-- TABELA: contador_os_diario
-- Contador sequencial de OS por cliente por dia
-- ============================================================================
CREATE TABLE IF NOT EXISTS contador_os_diario (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    data_contagem DATE NOT NULL,
    sequencial INTEGER DEFAULT 0,

    UNIQUE(cliente_id, data_contagem)
);

-- ============================================================================
-- Criar índices para performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_clientes_ativo ON clientes(ativo);
CREATE INDEX IF NOT EXISTS idx_ordens_data ON ordens_servico(data_criacao);
CREATE INDEX IF NOT EXISTS idx_fotos_ordem ON fotos(ordem_id);
CREATE INDEX IF NOT EXISTS idx_lancamentos_status ON lancamentos(status);

-- ============================================================================
-- Inserir cliente de teste (opcional)
-- ============================================================================
INSERT INTO clientes (nome, email, telefone, cpf_cnpj, endereco, cidade, estado, cep, ativo)
VALUES (
    'Cliente Teste',
    'teste@exemplo.com',
    '(11) 99999-9999',
    '12345678901234',
    'Rua Teste, 123',
    'São Paulo',
    'SP',
    '01310-100',
    TRUE
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- Commit
-- ============================================================================
COMMIT;
