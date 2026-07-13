# 🏪 Sistema de Gestão de Loja de Informática

**Migração moderna de VB6/Access → Python/React com suporte offline e sincronização automática**

- ✅ **Backend:** Python + FastAPI + PostgreSQL
- ✅ **Frontend:** React + Bootstrap (Web + Desktop via Electron)
- ✅ **Offline-First:** SQLite local + sincronização automática
- ✅ **Multiplataforma:** Windows + Linux + macOS

---

## 📋 Pré-Requisitos

### Windows
- Python 3.11+
- Node.js 18+ (npm)
- PostgreSQL 14+

### Linux
```bash
sudo apt update
sudo apt install -y python3.11 python3-pip nodejs npm postgresql postgresql-contrib
```

---

## 🚀 Instalação Rápida

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/projeto-loja.git
cd projeto-loja
```

### 2. Backend - Python/FastAPI

#### 2.1 Criar Ambiente Virtual
```bash
cd backend
python3 -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 2.2 Instalar Dependências
```bash
pip install -r requirements.txt
```

#### 2.3 Configurar Banco de Dados

**Linux/macOS:**
```bash
# Criar banco PostgreSQL
sudo -u postgres psql

CREATE DATABASE loja_informatica;
CREATE USER loja WITH PASSWORD 'senha123';
ALTER ROLE loja SET client_encoding TO 'utf8';
ALTER ROLE loja SET default_transaction_isolation TO 'read committed';
ALTER ROLE loja SET default_transaction_deferrable TO on;
ALTER ROLE loja SET default_time_zone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE loja_informatica TO loja;
\q
```

**Windows (COM instalador):**
Usar instalador `setup.exe` (em desenvolvimento)

#### 2.4 Configurar Variáveis de Ambiente
```bash
cp .env.example .env
# Editar .env com suas credenciais PostgreSQL
```

#### 2.5 Inicializar Banco
```bash
python main.py
# Tabelas serão criadas automaticamente
```

#### 2.6 Importar Dados do Access (Opcional)
```bash
python utils/etl_access.py \
  --cada /caminho/CADA.MDB \
  --os /caminho/OS.MDB \
  --caixa /caminho/CAIXA.MDB
```

#### 2.7 Iniciar Backend
```bash
python main.py
# API rodando em http://localhost:8000
# Swagger docs em http://localhost:8000/docs
```

---

### 3. Frontend - React

#### 3.1 Instalar Dependências
```bash
cd ../frontend
npm install
```

#### 3.2 Configurar Variáveis
```bash
cp .env.example .env.local
# REACT_APP_API_URL=http://localhost:8000 (padrão)
```

#### 3.3 Iniciar Dev Server
```bash
npm start
# Abrirá http://localhost:3000 automaticamente
```

---

## 📊 Estrutura do Projeto

```
projeto-loja/
│
├── backend/
│   ├── main.py                 # App FastAPI principal
│   ├── config.py               # Configurações
│   ├── database.py             # SQLAlchemy setup
│   ├── models.py               # Modelos ORM
│   ├── schemas.py              # Pydantic schemas
│   ├── requirements.txt
│   ├── routes/
│   │   ├── clientes.py         # CRUD Clientes
│   │   ├── ordens.py           # CRUD Ordens
│   │   ├── financeiro.py       # CRUD Financeiro
│   │   └── sync.py             # Sincronização
│   ├── utils/
│   │   ├── etl_access.py       # Importar do Access
│   │   └── sync_engine.py
│   └── .env.example
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── index.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ClientesPage.jsx
│   │   │   ├── OrdensPage.jsx
│   │   │   └── FinanceiroPage.jsx
│   │   ├── components/
│   │   │   ├── ClienteForm.jsx
│   │   │   ├── OrdemForm.jsx
│   │   │   └── RelatorioModal.jsx
│   │   ├── services/
│   │   │   └── api.js          # API client + offline sync
│   │   ├── styles/
│   │   │   └── Dashboard.css
│   │   └── utils/
│   ├── package.json
│   └── .env.example
│
├── installer/
│   └── setup.py                # Instalador inteligente
│
├── PROJETO_MIGRACAO_ACCESS_v1.md
└── README.md
```

---

## 🔄 Fluxo Offline-First

### Cliente Online
```
React → Fetch API → FastAPI → PostgreSQL
                   ↓
            Salvar em IndexedDB (cache)
```

### Cliente Offline
```
React → Service Worker → IndexedDB (local)
              ↓
        Fila de operações (sync_queue)
```

### Cliente Reconecta
```
Fila → POST /api/sync/push → FastAPI → PostgreSQL
           ↓
    Sincronizar IndexedDB
```

---

## 📱 Endpoints da API

### Clientes
```
GET    /api/clientes/              # Listar
POST   /api/clientes/              # Criar
GET    /api/clientes/{id}          # Obter
PUT    /api/clientes/{id}          # Atualizar
DELETE /api/clientes/{id}          # Deletar
GET    /api/clientes/stats/total   # Estatísticas
```

### Ordens
```
GET    /api/ordens/                # Listar
POST   /api/ordens/                # Criar
GET    /api/ordens/{id}            # Obter
PUT    /api/ordens/{id}            # Atualizar
DELETE /api/ordens/{id}            # Deletar
POST   /api/ordens/{id}/itens      # Adicionar item
DELETE /api/ordens/{id}/itens/{item_id}  # Remover item
GET    /api/ordens/stats/resumo    # Estatísticas
```

### Financeiro
```
GET    /api/financeiro/            # Listar
POST   /api/financeiro/            # Criar
GET    /api/financeiro/{id}        # Obter
PUT    /api/financeiro/{id}        # Atualizar
DELETE /api/financeiro/{id}        # Deletar
GET    /api/financeiro/relatorio/saldo         # Saldo
GET    /api/financeiro/relatorio/por-categoria # Por categoria
PUT    /api/financeiro/{id}/baixar # Marcar como baixado
```

### Sincronização
```
POST   /api/sync/push   # Enviar fila offline
GET    /api/sync/status # Status da fila
```

---

## 🧪 Testes

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

---

## 📦 Build/Deploy

### Backend - Build para Produção
```bash
cd backend
pip freeze > requirements.txt
# Usar Gunicorn em produção
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Frontend - Build para Produção
```bash
cd frontend
npm run build
# Arquivos em frontend/build/
# Servir com nginx/apache
```

### Desktop - Empacotar com Electron
```bash
cd frontend
npm install electron electron-builder --save-dev
npm run electron-build
# Gera loja-informatica-1.0.0.exe
```

---

## 🔐 Segurança

- ✅ Validação de entrada (Pydantic + React validation)
- ✅ CORS configurado corretamente
- ✅ Senhas com hash (bcrypt - em próxima fase)
- ✅ Logs de auditoria em BD
- ✅ Rate limiting (Planned)

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
cd backend
pip install -r requirements.txt
```

### "Connection refused: localhost:8000"
```bash
# Verificar se API está rodando
curl http://localhost:8000/health

# Se não, iniciar:
cd backend && python main.py
```

### "Cannot find module 'react'"
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Banco de dados não conecta
```bash
# Linux - verificar PostgreSQL
sudo systemctl status postgresql

# Criar banco se não existe
sudo -u postgres psql -c "CREATE DATABASE loja_informatica;"
```

---

## 📞 Suporte

- **Issues:** https://github.com/seu-usuario/projeto-loja/issues
- **Documentação:** /docs/
- **Email:** seu-email@seu-dominio.com

---

## 📄 Licença

MIT - Veja LICENSE.md

---

## 🗓️ Roadmap

- [x] Estrutura base (backend + frontend)
- [x] CRUD Clientes/Ordens/Financeiro
- [ ] Importação do Access (ETL)
- [ ] Sincronização offline-first
- [ ] Autenticação (Login)
- [ ] Relatórios PDF/Excel
- [ ] Dashboard avançado
- [ ] Packaging Electron
- [ ] Testes unitários
- [ ] Docker compose

---

**Versão 1.0.0 - Em desenvolvimento** 🚀
