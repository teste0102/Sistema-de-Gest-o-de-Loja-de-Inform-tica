-- ============================================================================
-- MIGRATION 003: ASSISTENTE DE CADASTRO DE OS (WIZARD)
-- Adiciona campos de endereço, produto, problema e assinatura do cliente.
-- Seguro: usa ADD COLUMN IF NOT EXISTS (não perde dados existentes).
-- ============================================================================

-- Produto (assistente de cadastro)
ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS produto_tipo VARCHAR(30);
ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS produto_descricao VARCHAR(255);

-- Endereço / Contato
ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS endereco_rua VARCHAR(150);
ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS endereco_tipo VARCHAR(20);
ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS endereco_complemento VARCHAR(120);
ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS endereco_numero VARCHAR(20);
ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS bairro VARCHAR(80);
ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS cidade_os VARCHAR(80);
ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS telefone_contato VARCHAR(20);

-- Problema relatado
ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS problema_descricao TEXT;

-- Assinatura digital do cliente (base64 PNG)
ALTER TABLE ordens_servico ADD COLUMN IF NOT EXISTS assinatura_cliente TEXT;
