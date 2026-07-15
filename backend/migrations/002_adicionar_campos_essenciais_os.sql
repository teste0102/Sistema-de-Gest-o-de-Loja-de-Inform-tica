-- Migração 002: Adicionar campos essenciais à Ordem de Serviço
-- Data: 2026-07-15
-- Propósito: Adicionar marca, modelo, IMEI, replay_dados e laudo_técnico

BEGIN;

-- Adicionar campos de dispositivo
ALTER TABLE ordens_servico
ADD COLUMN marca VARCHAR(60),
ADD COLUMN modelo VARCHAR(120),
ADD COLUMN imei VARCHAR(20) UNIQUE;

-- Criar índices para marca e modelo
CREATE INDEX idx_ordens_servico_marca ON ordens_servico(marca);
CREATE INDEX idx_ordens_servico_modelo ON ordens_servico(modelo);
CREATE INDEX idx_ordens_servico_imei ON ordens_servico(imei);

-- Adicionar campo de replay de digitação
ALTER TABLE ordens_servico
ADD COLUMN replay_dados TEXT;

-- Adicionar campos de laudo técnico
ALTER TABLE ordens_servico
ADD COLUMN laudo_assinatura_digital TEXT,
ADD COLUMN laudo_danos JSON,
ADD COLUMN laudo_data_criacao TIMESTAMP,
ADD COLUMN laudo_assinado_cliente BOOLEAN DEFAULT FALSE;

-- Criar índice para laudo
CREATE INDEX idx_ordens_servico_laudo_data ON ordens_servico(laudo_data_criacao);
CREATE INDEX idx_ordens_servico_laudo_assinado ON ordens_servico(laudo_assinado_cliente);

-- Adicionar trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_ordens_servico_updated_at ON ordens_servico;

CREATE TRIGGER update_ordens_servico_updated_at
BEFORE UPDATE ON ordens_servico
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- View: Ordens completas com todas as informações
DROP VIEW IF EXISTS v_ordens_completas;

CREATE VIEW v_ordens_completas AS
SELECT
    os.id,
    os.numero,
    os.numero_os,
    os.cliente_id,
    c.nome as cliente_nome,
    os.marca,
    os.modelo,
    os.imei,
    os.status,
    os.data_abertura,
    os.data_fechamento,
    COALESCE(os.senha_tipo, 'nenhuma') as senha_tipo,
    CASE WHEN os.replay_dados IS NOT NULL THEN TRUE ELSE FALSE END as tem_replay,
    CASE WHEN os.fotos IS NOT NULL THEN jsonb_array_length(os.fotos::jsonb) ELSE 0 END as total_fotos,
    CASE WHEN os.laudo_assinatura_digital IS NOT NULL THEN TRUE ELSE FALSE END as tem_laudo,
    os.laudo_assinado_cliente,
    os.created_at,
    os.updated_at
FROM ordens_servico os
LEFT JOIN clientes c ON os.cliente_id = c.id;

COMMIT;
