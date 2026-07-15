# 📋 Requisitos de OS (Ordem de Serviço) - CRÍTICOS NÃO IMPLEMENTADOS

**Status:** ⚠️ INCOMPLETO - Solicitado antes, não foi finalizado

---

## ✅ JÁ IMPLEMENTADO

- [x] Modelo de dados `OrdemServico` (OS)
- [x] Campos para senha (`senha_tipo`, `senha_cifrada`, `senha_imagem`)
- [x] Campos para fotos (`fotos` JSON array)
- [x] Webhooks para sincronização básica
- [x] Rota de sincronização de fotos
- [x] Rota de sincronização de senhas

---

## ❌ NÃO IMPLEMENTADO (CRÍTICO!)

### 1. **Criar Senhas (Backend)**
- [ ] Função para gerar senha PIN (4-6 dígitos)
- [ ] Função para gerar padrão (riscos)
- [ ] Função para "sem senha" (telefone desbloqueado)
- [ ] Armazenar com tipo definido
- [ ] Criptografar senha antes de armazenar
- [ ] **Endpoint POST `/api/os/{id}/senhas`**

### 2. **Replay da Digitação (Backend + Frontend)**
- [ ] Registrar sequência de toques (x, y, timestamp)
- [ ] Armazenar como JSON estruturado
- [ ] Reproduzir visualmente a digitação
- [ ] Campo `replay_dados` na tabela `OrdemServico`
- [ ] **Componente React para visualização**

### 3. **Fotos de Danos (Backend)**
- [ ] Pasta por cliente + número OS
- [ ] Armazenar múltiplas fotos
- [ ] Descrever tipo de dano (tela, botão, bateria, etc.)
- [ ] Geolocalização (opcional) da foto
- [ ] **Endpoint POST `/api/os/{id}/fotos`**
- [ ] **Endpoint DELETE `/api/os/{id}/fotos/{foto_id}`**

### 4. **Laudos com Danos (Backend + Frontend)**
- [ ] Modelo `LaudoTecnico` com campos:
  - Descrição de danos
  - Fotos associadas
  - Prognóstico/solução
  - Data do laudo
  - Técnico responsável
- [ ] **Endpoint GET/POST `/api/os/{id}/laudo`**
- [ ] PDF com fotos e descrição
- [ ] Assinatura digital do técnico

### 5. **Geração de Números OS pelo Servidor**
- [ ] Função para gerar número único de OS
- [ ] Formato: `OS-{YYYYMMDD}-{sequencial}` ou similar
- [ ] Garantir unicidade no banco
- [ ] **Endpoint POST `/api/os/gerar-numero`**

### 6. **Sincronização de Banco de Dados em Rede**
- [ ] Configurar múltiplos servidores PostgreSQL
- [ ] Replicação de dados entre servidores
- [ ] Sincronização de senhas e fotos
- [ ] Tratamento de conflitos
- [ ] Fallback para modo offline
- [ ] **Tabela de configuração de servidores remotos**

### 7. **Pasta por Cliente**
- [ ] Estrutura: `/uploads/clientes/{cliente_id}/os-{numero_os}/`
- [ ] Fotos organizadas por data
- [ ] Backup automático
- [ ] Controle de permissões (cliente só vê seus dados)

### 8. **Informações do Telefone Danificado**
- [ ] Modelo e marca do aparelho
- [ ] Estado físico (% bateria, água, queda)
- [ ] Problemas reportados vs encontrados
- [ ] Fotos de cada tipo de dano
- [ ] Checklist de verificação

---

## 📊 Estrutura de Dados Necessária

### Tabela: `OrdemServico` (modificar)
```sql
ALTER TABLE ordem_servico ADD COLUMN (
  numero_os VARCHAR(20) UNIQUE NOT NULL,
  cliente_id INTEGER,
  
  -- Senhas
  senha_tipo VARCHAR(20),           -- 'pin', 'padrao', 'nenhuma', 'biometria'
  senha_valor VARCHAR(255),          -- criptografada
  replay_dados JSON,                 -- [{x,y,tempo}, ...]
  
  -- Fotos
  fotos JSON,                        -- [{id, url, descricao, tipo_dano, data}, ...]
  
  -- Laudo
  laudo_descricao TEXT,
  laudo_data DATETIME,
  laudo_tecnico VARCHAR(100),
  
  -- Danos
  tem_tela_danificada BOOLEAN,
  tem_agua BOOLEAN,
  tem_queda BOOLEAN,
  observacoes_danos TEXT
);
```

### Tabela: `LaudoTecnico` (criar)
```sql
CREATE TABLE laudo_tecnico (
  id SERIAL PRIMARY KEY,
  numero_os VARCHAR(20),
  descricao TEXT,
  prognóstico VARCHAR(50),
  fotos_associadas JSON,
  data_laudo DATETIME,
  tecnico_id INTEGER,
  assinatura_digital TEXT
);
```

### Tabela: `ServidorRemoto` (criar)
```sql
CREATE TABLE servidor_remoto (
  id SERIAL PRIMARY KEY,
  nome VARCHAR(100),
  url VARCHAR(255),
  porta INTEGER,
  usuario VARCHAR(100),
  senha_cifrada VARCHAR(255),
  ativo BOOLEAN,
  ultima_sincronizacao DATETIME
);
```

---

## 🔗 Endpoints Necessários

```
POST   /api/os/gerar-numero              # Gera novo número OS
POST   /api/os/{id}/senhas               # Adiciona senha
GET    /api/os/{id}/senhas               # Visualiza replay
DELETE /api/os/{id}/senhas/{senha_id}    # Remove senha

POST   /api/os/{id}/fotos                # Upload de foto
GET    /api/os/{id}/fotos                # Lista fotos
DELETE /api/os/{id}/fotos/{foto_id}      # Remove foto

POST   /api/os/{id}/laudo                # Cria laudo técnico
GET    /api/os/{id}/laudo                # Busca laudo
PUT    /api/os/{id}/laudo                # Atualiza laudo

GET    /api/os/{id}/export-pdf           # Exporta OS com fotos e laudo

POST   /api/sync/servidor-remoto         # Registra servidor remoto
POST   /api/sync/push-remoto             # Sincroniza com servidor remoto
```

---

## 🎯 Componentes React Necessários

- [ ] `FormCriarSenha.jsx` - Escolher tipo (PIN/Padrão/Nenhuma)
- [ ] `ReplayDigitacao.jsx` - Visualizar digitação em replay
- [ ] `UploadFotos.jsx` - Upload múltiplo com descrição de dano
- [ ] `LaudoForm.jsx` - Criar laudo técnico
- [ ] `DanosChecklist.jsx` - Checklist de danos
- [ ] `VisualizadorOS.jsx` - Visualizar toda OS com fotos e laudo

---

## 📝 Notas Importantes

⚠️ **NÃO ESQUECER:**
- Senhas devem ser **CRIPTOGRAFADAS** no banco
- Fotos devem ter **BACKUP** em múltiplos locais
- Números OS devem ser **ÚNICOS** e **SEQUENCIAIS**
- Sincronização deve funcionar em modo **OFFLINE-FIRST**
- Cada cliente vê **APENAS SUAS OS**
- Laudos devem ser **IMUTÁVEIS** (criar novo em vez de editar)

---

**Última atualização:** 2026-07-15
**Prioridade:** 🔴 CRÍTICA - Bloqueia funcionalidade principal do sistema
