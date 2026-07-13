# ⚡ COMECE AGORA - Guia Rápido

**Tempo total: 10-15 minutos para estar rodando**

---

## 📦 O QUE FOI CRIADO

```
projeto-loja/                    (seu projeto)
├── backend/                      Python + FastAPI
│   ├── main.py                  API pronta
│   ├── models.py                BD schemas
│   ├── routes/                  Endpoints (clientes, ordens, financeiro)
│   └── requirements.txt          Dependências
│
├── frontend/                     React moderno
│   ├── src/App.jsx              App principal
│   ├── src/pages/               4 telas prontas
│   ├── src/services/api.js      Cliente com offline-sync
│   └── package.json
│
├── docker-compose.yml            PostgreSQL + pgAdmin
├── start.sh                       Script de início
└── README.md                      Documentação completa
```

---

## 🚀 INÍCIO RÁPIDO (Linux/macOS)

### Opção 1: Automática (Recomendado)
```bash
cd projeto-loja
chmod +x start.sh
./start.sh
# Tudo inicia automaticamente! 🎉
```

### Opção 2: Manual (Controle total)

#### Terminal 1 - PostgreSQL (se tiver Docker)
```bash
cd projeto-loja
docker-compose up postgres pgadmin
# PostgreSQL rodando em localhost:5432
# pgAdmin em http://localhost:5050
```

#### Terminal 2 - Backend
```bash
cd projeto-loja/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
# API em http://localhost:8000 ✅
# Swagger em http://localhost:8000/docs 📚
```

#### Terminal 3 - Frontend
```bash
cd projeto-loja/frontend
npm install
npm start
# Web em http://localhost:3000 ✅
```

---

## 🎯 AGORA VOCÊ TEM

| Recurso | URL | O Que Faz |
|---------|-----|----------|
| **API** | http://localhost:8000 | Backend Python/FastAPI |
| **Swagger** | http://localhost:8000/docs | Documentação interativa |
| **Web** | http://localhost:3000 | Frontend React |
| **pgAdmin** | http://localhost:5050 | Gerenciar PostgreSQL |

---

## 📚 PRÓXIMOS PASSOS

### 1️⃣ Testar a API
```bash
curl http://localhost:8000/health
# Resposta: {"status":"healthy", "database":"ok", ...}
```

### 2️⃣ Acessar Web
Abra http://localhost:3000 no navegador → deve ver **Dashboard** com estatísticas

### 3️⃣ Criar Primeiro Cliente
```bash
curl -X POST http://localhost:8000/api/clientes/ \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": 1,
    "nome": "Teste Ltda",
    "telefone": "11-99999999",
    "email": "teste@exemplo.com"
  }'
```

### 4️⃣ Ver no Dashboard
Acesse http://localhost:3000 → guia **Clientes** → verá o cliente criado

---

## 🔄 PRÓXIMAS FASES (Roadmap)

- [ ] Importar dados do Access (ETL)
- [ ] Autenticação (Login/Senha)
- [ ] Relatórios (PDF/Excel)
- [ ] Sincronização Offline-First
- [ ] Empacotar como .exe (Electron)
- [ ] Testes automatizados

---

## 🛠️ COMANDOS ÚTEIS

### Backend
```bash
cd backend
source venv/bin/activate

# Criar/resetar BD
python main.py

# Importar Access (depois)
python utils/etl_access.py --cada /path/CADA.MDB --os /path/OS.MDB

# Testes
pytest
```

### Frontend
```bash
cd frontend

# Desenvolvimento
npm start

# Build produção
npm run build

# Testes
npm test
```

### PostgreSQL (Docker)
```bash
# Ver logs
docker-compose logs postgres

# Conectar ao BD
docker-compose exec postgres psql -U loja -d loja_informatica

# Parar tudo
docker-compose down
```

---

## 🐛 ERROS COMUNS

### ❌ "Module not found: fastapi"
**Solução:** `pip install -r requirements.txt`

### ❌ "Cannot find module 'react'"
**Solução:** `cd frontend && npm install`

### ❌ "Connection refused: localhost:5432"
**Solução:** `docker-compose up postgres` ou iniciar PostgreSQL local

### ❌ "Porta 3000 já em uso"
**Solução:** `kill $(lsof -t -i:3000)` ou `PORT=3001 npm start`

### ❌ "Porta 8000 já em uso"
**Solução:** `kill $(lsof -t -i:8000)` ou `python -m uvicorn main:app --port 8001`

---

## 📊 ARQUITETURA FINAL

```
┌─────────────────────────────────────┐
│  USUÁRIO (Browser/Desktop)          │
│  http://localhost:3000 (React)      │
└──────────────┬──────────────────────┘
               │
               ↓
        ┌─────────────────┐
        │  Offline Sync   │
        │  (IndexedDB)    │
        └────────┬────────┘
                 │
                 ↓
    ┌────────────────────────┐
    │  FastAPI Backend       │
    │  localhost:8000        │
    │  ├─ /api/clientes      │
    │  ├─ /api/ordens        │
    │  ├─ /api/financeiro    │
    │  └─ /api/sync          │
    └────────────┬───────────┘
                 │
                 ↓
    ┌────────────────────────┐
    │  PostgreSQL Database   │
    │  localhost:5432        │
    └────────────────────────┘
```

---

## ✨ FEATURES JÁ IMPLEMENTADAS

✅ Backend completo (FastAPI)
✅ BD com 8 tabelas (SQLAlchemy)
✅ Frontend com 4 telas (React)
✅ API REST completa
✅ Sincronização offline (arquitetura)
✅ CORS configurado
✅ Swagger docs automático
✅ Suporte Windows/Linux/macOS

---

## 📞 PRECISA DE AJUDA?

1. **Documentação:** `/projeto-loja/README.md`
2. **Arquitetura:** `/PROJETO_MIGRACAO_ACCESS_v1.md`
3. **API Docs:** http://localhost:8000/docs (quando rodando)
4. **VS Code Extensions:**
   - Python (Microsoft)
   - Pylance
   - ES7+ React/Redux
   - REST Client

---

## 🎉 PARABÉNS!

Você tem agora um sistema moderno, escalável e profissional! 

**Próximas ações:**
1. Teste as APIs pelo Swagger
2. Explore o frontend
3. Comece a integrar dados do Access
4. Customize conforme necessário

---

**Versão 1.0.0** | Última atualização: Julho 2026 | Status: ✅ PRONTO
