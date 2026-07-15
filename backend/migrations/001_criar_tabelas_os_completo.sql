-- Migração: Criar tabelas para sistema completo de OS
-- Data: 2026-07-15
-- Versão: 1.0

-- ============================================================================
-- FASE 0: TABELAS BASE
-- ============================================================================

-- Adicionar campos na tabela ordens_servico
ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS (
  numero_os VARCHAR(20) UNIQUE NOT NULL DEFAULT 'TEMP',
  replay_dados JSONB,
  laudo_assinatura_digital TEXT
);

-- Criar índice para número OS (busca rápida)
CREATE INDEX IF NOT EXISTS idx_numero_os ON ordens_servico(numero_os);

-- ============================================================================
-- FASE 1: SENHAS E REPLAY
-- ============================================================================

-- Tabela para Replay de Digitação
CREATE TABLE IF NOT EXISTS replay_digitacao (
  id SERIAL PRIMARY KEY,
  ordem_id INTEGER NOT NULL,
  sequencia JSONB NOT NULL,                    -- [{x, y, t, tipo}, ...]
  duracao_ms INTEGER,
  dispositivo JSONB,                           -- {modelo, so, resolucao}
  criado_em TIMESTAMP DEFAULT NOW(),

  CONSTRAINT fk_replay_ordem FOREIGN KEY (ordem_id)
    REFERENCES ordens_servico(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_replay_ordem ON replay_digitacao(ordem_id);

-- ============================================================================
-- FASE 2: FOTOS E TIPOS DE DANO
-- ============================================================================

-- Catálogo de Tipos de Dano
CREATE TABLE IF NOT EXISTS tipos_dano (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(50) UNIQUE NOT NULL,
  descricao TEXT,
  icone VARCHAR(255),
  ativo BOOLEAN DEFAULT TRUE,
  criado_em TIMESTAMP DEFAULT NOW()
);

-- Dados iniciais de tipos de dano
INSERT INTO tipos_dano (nome, descricao, icone) VALUES
  ('tela', 'Tela danificada/trincada', '🔨'),
  ('botao', 'Botão danificado/preso', '🔘'),
  ('bateria', 'Bateria descarregada/inchada', '🔋'),
  ('agua', 'Dano por água/umidade', '💧'),
  ('queda', 'Dano por queda/impacto', '⬇️'),
  ('outro', 'Outro tipo de dano', '❓')
ON CONFLICT DO NOTHING;

-- Tabela de Fotos
CREATE TABLE IF NOT EXISTS fotos (
  id VARCHAR(50) PRIMARY KEY,                  -- UUID
  ordem_id INTEGER NOT NULL,
  tipo_dano VARCHAR(50),
  descricao TEXT,
  path_disco VARCHAR(500),
  path_thumbnail VARCHAR(500),
  url_publica VARCHAR(500),
  tamanho_bytes BIGINT,
  dimensoes JSONB,                             -- {largura, altura}
  dispositivo_info JSONB,                      -- {modelo, so, gps_lat?, gps_lon?}
  data_captura TIMESTAMP DEFAULT NOW(),
  criado_em TIMESTAMP DEFAULT NOW(),

  CONSTRAINT fk_foto_ordem FOREIGN KEY (ordem_id)
    REFERENCES ordens_servico(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_foto_ordem ON fotos(ordem_id);
CREATE INDEX IF NOT EXISTS idx_foto_tipo ON fotos(tipo_dano);

-- ============================================================================
-- FASE 3: LAUDO TÉCNICO
-- ============================================================================

-- Tabela de Laudo Técnico
CREATE TABLE IF NOT EXISTS laudo_tecnico (
  id SERIAL PRIMARY KEY,
  ordem_id INTEGER UNIQUE,
  numero_os VARCHAR(20),
  descricao_danos TEXT,
  prognóstico VARCHAR(100),                    -- reparável, não-reparável, análise-pendente
  solucao_proposta TEXT,
  valor_estimado NUMERIC(10, 2),
  fotos_associadas JSONB,                      -- [foto_id1, foto_id2, ...]
  checklist_danos JSONB,                       -- {tela: bool, botao: bool, ...}
  tecnico_id INTEGER,
  tecnico_nome VARCHAR(100),
  data_laudo TIMESTAMP DEFAULT NOW(),
  assinatura_digital TEXT,
  hash_integridade VARCHAR(255),
  imutavel BOOLEAN DEFAULT TRUE,
  criado_em TIMESTAMP DEFAULT NOW(),

  CONSTRAINT fk_laudo_ordem FOREIGN KEY (ordem_id)
    REFERENCES ordens_servico(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_laudo_ordem ON laudo_tecnico(ordem_id);
CREATE INDEX IF NOT EXISTS idx_laudo_numero_os ON laudo_tecnico(numero_os);

-- ============================================================================
-- FASE 4: SINCRONIZAÇÃO MULTI-SERVIDOR
-- ============================================================================

-- Tabela de Servidores Remotos
CREATE TABLE IF NOT EXISTS servidor_remoto (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(100) UNIQUE NOT NULL,
  tipo VARCHAR(20),                            -- postgresql, mysql, access
  host VARCHAR(255) NOT NULL,
  porta INTEGER DEFAULT 5432,
  usuario VARCHAR(100),
  senha_cifrada VARCHAR(500),
  banco_dados VARCHAR(100),
  ativo BOOLEAN DEFAULT TRUE,
  usar_replicacao BOOLEAN DEFAULT TRUE,
  url_conexao VARCHAR(1000),
  ultima_sincronizacao TIMESTAMP,
  status_conexao VARCHAR(50) DEFAULT 'desconhecido',
  mensagem_erro TEXT,
  prioridade INTEGER DEFAULT 1,                -- 1=principal, 2=backup, 3=fallback
  criado_em TIMESTAMP DEFAULT NOW(),
  atualizado_em TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_servidor_ativo ON servidor_remoto(ativo);
CREATE INDEX IF NOT EXISTS idx_servidor_prioridade ON servidor_remoto(prioridade);

-- Tabela de Histórico de Sincronização
CREATE TABLE IF NOT EXISTS sincronizacao_historico (
  id SERIAL PRIMARY KEY,
  servidor_id INTEGER,
  tipo_sincronizacao VARCHAR(50),              -- push, pull, bidirecional
  data_inicio TIMESTAMP DEFAULT NOW(),
  data_fim TIMESTAMP,
  registros_processados INTEGER DEFAULT 0,
  registros_com_conflito INTEGER DEFAULT 0,
  registros_com_erro INTEGER DEFAULT 0,
  status VARCHAR(50),                          -- sucesso, parcial, erro
  mensagem TEXT,
  duracao_segundos FLOAT,

  CONSTRAINT fk_sync_servidor FOREIGN KEY (servidor_id)
    REFERENCES servidor_remoto(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sync_servidor ON sincronizacao_historico(servidor_id);
CREATE INDEX IF NOT EXISTS idx_sync_data ON sincronizacao_historico(data_inicio);

-- ============================================================================
-- TABELAS DE CONTROLE DE SINCRONIZAÇÃO OFFLINE
-- ============================================================================

-- Fila de Sincronização (se não existir)
CREATE TABLE IF NOT EXISTS sync_queue (
  id SERIAL PRIMARY KEY,
  tabela VARCHAR(100),
  operacao VARCHAR(20),                        -- insert, update, delete
  registro_id INTEGER,
  dados JSONB,
  conflito BOOLEAN DEFAULT FALSE,
  tentativas INTEGER DEFAULT 0,
  ultima_tentativa TIMESTAMP,
  criado_em TIMESTAMP DEFAULT NOW(),
  processado_em TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sync_queue_processado
  ON sync_queue(processado_em) WHERE processado_em IS NULL;

-- ============================================================================
-- CONSTRAINTS E SEGURANÇA
-- ============================================================================

-- Validação de prognóstico
ALTER TABLE laudo_tecnico ADD CONSTRAINT chk_prognostico
  CHECK (prognóstico IN ('reparável', 'não-reparável', 'análise-pendente'))
  NOT VALID;

-- Validação de tipo de sincronização
ALTER TABLE sincronizacao_historico ADD CONSTRAINT chk_tipo_sync
  CHECK (tipo_sincronizacao IN ('push', 'pull', 'bidirecional'))
  NOT VALID;

-- ============================================================================
-- VIEWS ÚTEIS
-- ============================================================================

-- View: Ordens com informações completas
CREATE OR REPLACE VIEW v_ordens_completas AS
SELECT
  os.id,
  os.numero_os,
  os.cliente_id,
  os.status,
  os.data_criacao,
  (SELECT COUNT(*) FROM fotos WHERE ordem_id = os.id) as total_fotos,
  (SELECT COUNT(*) FROM replay_digitacao WHERE ordem_id = os.id) as total_replays,
  CASE WHEN lt.id IS NOT NULL THEN true ELSE false END as tem_laudo,
  lt.prognóstico,
  lt.valor_estimado,
  os.updated_at
FROM ordens_servico os
LEFT JOIN laudo_tecnico lt ON os.id = lt.ordem_id
ORDER BY os.data_criacao DESC;

-- View: Sincronizações pendentes
CREATE OR REPLACE VIEW v_sync_pendentes AS
SELECT
  id,
  tabela,
  operacao,
  tentativas,
  criado_em,
  CASE
    WHEN tentativas = 0 THEN 'Nunca foi tentado'
    WHEN tentativas < 3 THEN 'Tentaremos novamente'
    ELSE 'Máximo de tentativas atingido'
  END as status
FROM sync_queue
WHERE processado_em IS NULL
ORDER BY criado_em ASC;

-- ============================================================================
-- GRANTS (Segurança - se usar usuário específico)
-- ============================================================================

-- Para usuário 'loja':
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO loja;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO loja;

-- ============================================================================
-- DADOS DE TESTE (opcional, remover em produção)
-- ============================================================================

-- Inserir servidor remoto de teste
-- INSERT INTO servidor_remoto (nome, tipo, host, porta, usuario, prioridade)
-- VALUES ('Servidor Backup', 'postgresql', 'backup.example.com', 5432, 'replicacao', 2);
