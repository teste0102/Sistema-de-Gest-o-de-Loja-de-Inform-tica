# 🚀 GUIA DE INSTALAÇÃO - Sistema de Gestão de Loja de Informática

## ✅ Pré-Requisitos Instalados

- ✅ Python 3.11+
- ✅ Node.js 22.22.2
- ✅ npm 10.9.7
- ✅ Docker 29.3.1
- ✅ Docker Compose v5.1.1

---

## 📦 INSTALAÇÃO RÁPIDA (Já Feita!)

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```
✅ **Status:** Instalado e validado

### Frontend
```bash
cd frontend
npm install
```
✅ **Status:** 1344 pacotes instalados com sucesso

---

## 🔧 CONFIGURAÇÃO DE AMBIENTE

### Backend (.env)
Arquivo criado automaticamente em `backend/.env` com as configurações:
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=loja
DB_PASSWORD=senha123
DB_NAME=loja_informatica
```

### Frontend (.env.local)
Arquivo criado automaticamente em `frontend/.env.local`:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENABLE_OFFLINE_SYNC=true
```

---

## 🗄️ INICIAR BANCO DE DADOS (PostgreSQL)

### Opção 1: Com Docker (Recomendado)
```bash
docker compose up -d postgres pgadmin
```
- PostgreSQL: `localhost:5432`
- pgAdmin: `http://localhost:5050`
- Credenciais padrão: loja / senha123

### Opção 2: PostgreSQL Local
Certifique-se de que PostgreSQL está rodando e criar o banco:
```bash
sudo -u postgres psql

CREATE DATABASE loja_informatica;
CREATE USER loja WITH PASSWORD 'senha123';
ALTER ROLE loja SET client_encoding TO 'utf8';
ALTER ROLE loja SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE loja_informatica TO loja;
\q
```

---

## 🎯 INICIAR A APLICAÇÃO

### Terminal 1: Backend (FastAPI)
```bash
cd backend
source venv/bin/activate
python main.py
```
- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Terminal 2: Frontend (React)
```bash
cd frontend
npm start
```
- Web App: `http://localhost:3000`

### OU Automático (Com tmux)
```bash
chmod +x start.sh
./start.sh
```

---

## ✅ TESTES RÁPIDOS

### Verificar se Backend está OK
```bash
curl http://localhost:8000/health
```
Resposta esperada:
```json
{
  "status": "healthy",
  "database": "ok",
  "system": "Linux",
  "timestamp": null
}
```

### Criar um Cliente (Teste)
```bash
curl -X POST http://localhost:8000/api/clientes/ \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": 1,
    "nome": "Teste Ltda",
    "telefone": "11-99999999",
    "email": "teste@email.com"
  }'
```

### Acessar API Interativa
Abra `http://localhost:8000/docs` no navegador para testar todas as rotas

---

## 📊 ESTRUTURA DO BANCO DE DADOS

Tabelas criadas automaticamente ao iniciar:
- `clientes` - Clientes da loja
- `ordens_servico` - Ordens de serviço
- `ordem_itens` - Itens de cada ordem
- `lancamentos` - Financeiro (receitas e despesas)
- `sync_queue` - Fila de sincronização offline
- `audit_log` - Log de auditoria

---

## 🐛 TROUBLESHOOTING

### Erro: "Connection refused: localhost:5432"
**Solução:** Certifique-se que PostgreSQL está rodando
```bash
docker compose up postgres
# ou se local:
sudo systemctl start postgresql
```

### Erro: "ModuleNotFoundError: No module named 'fastapi'"
**Solução:** Ativar ambiente virtual e instalar dependências
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "Cannot find module 'react'"
**Solução:** Reinstalar dependências
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Porta 3000 ou 8000 já em uso
**Solução:**
```bash
# Matar processo na porta 3000
kill $(lsof -t -i :3000)

# Matar processo na porta 8000
kill $(lsof -t -i :8000)
```

---

## 📚 ENDPOINTS PRINCIPAIS DA API

| Método | URL | Descrição |
|--------|-----|----------|
| GET | `/health` | Verificar saúde da API |
| GET | `/api/clientes` | Listar clientes |
| POST | `/api/clientes` | Criar cliente |
| GET | `/api/ordens` | Listar ordens |
| POST | `/api/ordens` | Criar ordem |
| GET | `/api/financeiro` | Listar lançamentos |
| POST | `/api/sync/push` | Sincronizar dados offline |

Documentação completa em: `http://localhost:8000/docs`

---

## 🔐 SEGURANÇA

- ✅ CORS configurado corretamente
- ✅ Validação de entrada com Pydantic
- ⚠️ Senhas sem hash (implementar em próxima fase)
- ⚠️ Sem autenticação/login (implementar em próxima fase)

---

## 📁 ESTRUTURA DO PROJETO

```
projeto-loja/
├── backend/
│   ├── main.py                # App FastAPI
│   ├── config.py              # Configurações
│   ├── models.py              # Modelos SQLAlchemy
│   ├── database.py            # Conexão BD
│   ├── schemas.py             # Validação Pydantic
│   ├── routes/                # Endpoints API
│   ├── requirements.txt        # Dependências
│   ├── .env.example           # Exemplo de env
│   └── venv/                  # Ambiente virtual
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Componente principal
│   │   ├── pages/             # Páginas (Dashboard, Clientes, etc)
│   │   ├── components/        # Componentes reutilizáveis
│   │   ├── services/          # Cliente API + sync
│   │   └── styles/            # CSS/SCSS
│   ├── package.json           # Dependências npm
│   ├── .env.example           # Exemplo de env local
│   └── node_modules/          # Pacotes npm
│
├── docker-compose.yml         # PostgreSQL + pgAdmin
├── start.sh                   # Script automático
├── README.md                  # Documentação
├── INSTALACAO.md              # Este arquivo
└── .gitignore                 # Arquivos ignorados
```

---

## 🗓️ Roadmap

- [x] Estrutura base (backend + frontend)
- [x] CRUD Clientes/Ordens/Financeiro
- [x] Banco de dados PostgreSQL
- [x] Docker Compose
- [ ] Importação do Access (ETL)
- [ ] Autenticação (Login/Senha)
- [ ] Sincronização offline-first completa
- [ ] Relatórios PDF/Excel
- [ ] Dashboard avançado
- [ ] Testes unitários
- [ ] Packaging Electron (.exe)

---

## 📞 Suporte

- **Documentação:** Veja README.md
- **API Docs:** http://localhost:8000/docs
- **Issues:** GitHub Issues

---

**Versão 1.0.0 - Julho 2026** ✅ Pronto para uso!
