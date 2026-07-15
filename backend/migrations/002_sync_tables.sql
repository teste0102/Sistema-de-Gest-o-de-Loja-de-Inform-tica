-- ============================================================================
-- MIGRATION 002: SYNC TABLES
-- Tabelas para sincronização multi-servidor e offline-first
-- ============================================================================

-- ============================================================================
-- TABELA: sync_queue
-- Fila de sincronização com resolução de conflitos
-- ============================================================================
CREATE TABLE IF NOT EXISTS sync_queue (
    id SERIAL PRIMARY KEY,
    tabela VARCHAR(50) NOT NULL,
    operacao VARCHAR(20) NOT NULL,
    registro_id INTEGER NOT NULL,
    dados_json TEXT,
    hash_dados VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'pendente',
    tentativas INTEGER DEFAULT 0,
    erro_mensagem TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_sincronizacao TIMESTAMP,
    sincronizado BOOLEAN DEFAULT FALSE
);

-- ============================================================================
-- TABELA: servidores_remotos
-- Registro de servidores para sincronização
-- ============================================================================
CREATE TABLE IF NOT EXISTS servidores_remotos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    url VARCHAR(500) NOT NULL,
    chave_api_cifrada TEXT NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    ultima_sincronizacao TIMESTAMP,
    status_conexao VARCHAR(20) DEFAULT 'desconectado',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABELA: conflitos_sync
-- Registro de conflitos detectados durante sincronização
-- ============================================================================
CREATE TABLE IF NOT EXISTS conflitos_sync (
    id SERIAL PRIMARY KEY,
    tabela VARCHAR(50) NOT NULL,
    registro_id INTEGER NOT NULL,
    dados_local TEXT,
    dados_remoto TEXT,
    tipo_conflito VARCHAR(50),
    estrategia_resolucao VARCHAR(50),
    dados_resolvidos TEXT,
    resolvido BOOLEAN DEFAULT FALSE,
    data_deteccao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_resolucao TIMESTAMP
);

-- ============================================================================
-- TABELA: historico_sincronizacao
-- Histórico completo de sincronizações realizadas
-- ============================================================================
CREATE TABLE IF NOT EXISTS historico_sincronizacao (
    id SERIAL PRIMARY KEY,
    servidor_id INTEGER REFERENCES servidores_remotos(id) ON DELETE CASCADE,
    operacoes_enviadas INTEGER DEFAULT 0,
    operacoes_recebidas INTEGER DEFAULT 0,
    conflitos_resolvidos INTEGER DEFAULT 0,
    erros_ocorridos INTEGER DEFAULT 0,
    duracao_ms INTEGER,
    resultado VARCHAR(20),
    mensagem TEXT,
    data_sincronizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABELA: cache_offline
-- Cache de dados para acesso offline
-- ============================================================================
CREATE TABLE IF NOT EXISTS cache_offline (
    id SERIAL PRIMARY KEY,
    entidade VARCHAR(50) NOT NULL,
    entidade_id INTEGER NOT NULL,
    dados_json TEXT,
    hash_dados VARCHAR(100),
    versao INTEGER DEFAULT 1,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(entidade, entidade_id)
);

-- ============================================================================
-- TABELA: configuracoes_sincronizacao
-- Configurações globais de sincronização
-- ============================================================================
CREATE TABLE IF NOT EXISTS configuracoes_sincronizacao (
    id SERIAL PRIMARY KEY,
    chave VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT,
    tipo_valor VARCHAR(20),
    descricao TEXT,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Inserir configurações padrão
-- ============================================================================
INSERT INTO configuracoes_sincronizacao (chave, valor, tipo_valor, descricao) VALUES
('INTERVALO_SYNC_SEGUNDOS', '300', 'integer', 'Intervalo de sincronização automática em segundos'),
('TIMEOUT_REQUISICAO_SEGUNDOS', '30', 'integer', 'Timeout para requisições de sincronização'),
('MAX_TENTATIVAS_ERRO', '3', 'integer', 'Máximo de tentativas antes de marcar como erro'),
('ESTRATEGIA_PADRAO', 'merge_timestamps', 'string', 'Estratégia padrão para resolução de conflitos'),
('MODO_OFFLINE', 'true', 'boolean', 'Ativa modo offline-first'),
('SINCRONIZAR_FOTOS', 'true', 'boolean', 'Sincronizar dados de fotos'),
('TAMANHO_MAX_FILA', '10000', 'integer', 'Tamanho máximo da fila de sincronização')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- Criar índices para performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_sync_queue_estado ON sync_queue(estado);
CREATE INDEX IF NOT EXISTS idx_conflitos_resolvido ON conflitos_sync(resolvido);
CREATE INDEX IF NOT EXISTS idx_cache_offline_entidade ON cache_offline(entidade);
CREATE INDEX IF NOT EXISTS idx_historico_sincronizacao ON historico_sincronizacao(servidor_id);

-- ============================================================================
-- Commit
-- ============================================================================
COMMIT;
