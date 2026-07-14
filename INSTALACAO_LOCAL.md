# 🚀 INSTALAÇÃO LOCAL - Sistema Híbrido FastAPI + Node.js

**⚠️ IMPORTANTE:** Este guia é para rodar os servidores **NO SEU PC**, não na nuvem.

**⏱️ Tempo total: 10-15 minutos**

---

## ✅ Pré-Requisitos (Obrigatório)

Você precisa ter instalado no seu computador:

- ✅ **Python 3.11+** - [Baixar](https://www.python.org/downloads/)
- ✅ **Node.js 18+** - [Baixar](https://nodejs.org/)
- ✅ **PostgreSQL 13+** - [Baixar](https://www.postgresql.org/download/)
- ✅ **Git** - [Baixar](https://git-scm.com/download)
- ✅ **Docker Desktop** - [Baixar](https://www.docker.com/products/docker-desktop) (RECOMENDADO para PostgreSQL)

---

## 📍 OPÇÃO 1: Instalação com Docker (RECOMENDADO - Mais Fácil)

### Passo 1: Verificar se Docker está instalado

```bash
docker --version
docker-compose --version
```

Se não tiver Docker, instale em: https://www.docker.com/products/docker-desktop

### Passo 2: Iniciar PostgreSQL com Docker

Na pasta do projeto, execute:

```bash
docker-compose up -d postgres
```

**Resultado esperado:**
- PostgreSQL rodando em `localhost:5432`
- Usuário: `postgres`
- Senha: `postgres`
- Banco: `loja_informatica`

Para verificar se está rodando:
```bash
docker ps
```

---

## 📍 OPÇÃO 2: Instalação Manual com PostgreSQL Local

Se não quer usar Docker, instale PostgreSQL localmente:

1. Acesse https://www.postgresql.org/download/
2. Instale a versão 13 ou superior
3. Durante a instalação:
   - Senha para usuário `postgres`: `postgres`
   - Porta: `5432`

Após instalar, abra o terminal e execute:

```bash
# Criar banco de dados
createdb -U postgres loja_informatica

# Verificar se criou
psql -U postgres -l
```

---

## 🔧 PASSO 1: Clonar/Atualizar Repositório

Se NÃO clonou ainda:

```bash
git clone https://github.com/teste0102/Sistema-de-Gest-o-de-Loja-de-Inform-tica.git
cd Sistema-de-Gest-o-de-Loja-de-Inform-tica
```

Se já clonou, atualize:

```bash
cd Sistema-de-Gest-o-de-Loja-de-Inform-tica
git pull origin main
```

---

## 🔧 PASSO 2: Instalar Dependências do Backend (FastAPI)

Abra um **Terminal/PowerShell** e execute:

### Windows:

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Linux/macOS:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Se `requirements.txt` não existir**, instale manualmente:

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-multipart requests email-validator
```

---

## 🔧 PASSO 3: Instalar Dependências do Frontend (Node.js)

Abra **outro Terminal/PowerShell** e execute:

```bash
cd /workspace/atendimento
npm install
```

**Se a pasta `/workspace/atendimento` não existir** (em Windows), procure por:

```bash
# Windows - procurar a pasta atendimento
dir "atendimento" /s

# Linux/macOS
find . -name "atendimento" -type d
```

Se ainda assim não encontrar, o projeto atendimento está em:
- Geralmente: `C:\workspace\atendimento` (Windows)
- Ou: `/workspace/atendimento` (Linux/macOS)

---

## 🚀 PASSO 4: Iniciar os Servidores

Você precisa abrir **3 Terminais/PowerShells diferentes**:

---

### ✅ Terminal 1️⃣ - PostgreSQL (só se usar Docker)

```bash
cd Sistema-de-Gest-o-de-Loja-de-Inform-tica
docker-compose up postgres
```

Deixe rodando. Resultado esperado:
```
postgres_1  | ready to accept connections
```

---

### ✅ Terminal 2️⃣ - FastAPI (Backend)

```bash
cd Sistema-de-Gest-o-de-Loja-de-Inform-tica/backend

# Windows
venv\Scripts\activate
python main.py

# Linux/macOS
source venv/bin/activate
python main.py
```

**Ou com uvicorn diretamente:**

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Resultado esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ FastAPI estará disponível em: **http://localhost:8000**

---

### ✅ Terminal 3️⃣ - Node.js (Atendimento - Ordem de Serviço)

```bash
cd /workspace/atendimento
node server/index.js
```

**Resultado esperado:**
```
========================================================
  App ATENDIMENTO (Ordem de Servico) rodando
  Neste PC:   http://localhost:3000
  Modo:       production
  Dados em:   ./data
========================================================
```

✅ Node.js estará disponível em: **http://localhost:3000**

---

## 🌐 PASSO 5: Acessar as Interfaces

Abra seu navegador e acesse:

### 1️⃣ **Interface de Atendimento (Node.js)**
- URL: http://localhost:3000/
- O que é: Sistema para criar e editar Ordens de Serviço
- Função: Adicionar fotos, vídeos, senhas

### 2️⃣ **API FastAPI (Backend)**
- URL: http://localhost:8000/
- Docs interativa: http://localhost:8000/docs
- Função: API de clientes, ordens, webhooks

### 3️⃣ **Health Check - Verificar se está tudo rodando**

```bash
# FastAPI
curl http://localhost:8000/health

# Node.js
curl http://localhost:3000/api/webhook/health
```

---

## ✅ PASSO 6: Testar Funcionamento

### Teste 1: Criar um Cliente

```bash
curl -X POST http://localhost:8000/api/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": 1,
    "nome": "João Silva",
    "telefone": "11999999999",
    "email": "joao@example.com"
  }'
```

**Resposta esperada:**
```json
{
  "id": 1,
  "codigo": 1,
  "nome": "João Silva",
  "telefone": "11999999999",
  "email": "joao@example.com",
  "created_at": "2026-07-14T...",
  "updated_at": "2026-07-14T..."
}
```

### Teste 2: Criar uma Ordem de Serviço

```bash
curl -X POST http://localhost:8000/api/ordens \
  -H "Content-Type: application/json" \
  -d '{
    "numero": 1,
    "cliente_id": 1,
    "descricao": "Trocar bateria do celular",
    "data_abertura": "2026-07-14",
    "status": "aberto",
    "tecnico": "Carlos"
  }'
```

**Resposta esperada:**
```json
{
  "id": 1,
  "numero": 1,
  "cliente_id": 1,
  "descricao": "Trocar bateria do celular",
  "status": "aberto",
  "created_at": "2026-07-14T...",
  "updated_at": "2026-07-14T..."
}
```

Se ambos funcionarem, **está tudo pronto!** ✅

---

## 🐛 Troubleshooting - Problemas Comuns

### ❌ "Python não encontrado"

**Solução:**
- Instale Python 3.11+ em https://www.python.org/
- **IMPORTANTE:** Durante a instalação, marque ✅ "Add Python to PATH"
- Reinicie o Terminal/PowerShell

### ❌ "pip: comando não encontrado"

```bash
# Windows
python -m pip install --upgrade pip

# Linux/macOS
python3 -m pip install --upgrade pip
```

### ❌ "Connection refused: localhost:5432"

**Solução:**
- Certifique-se de que PostgreSQL está rodando:
  ```bash
  docker ps  # Se usar Docker
  ```
- Ou inicie o serviço PostgreSQL local

### ❌ "Porta 3000 já em uso"

**Solução:**
```bash
# Encontrar processo usando porta 3000
# Windows
netstat -ano | findstr :3000

# Linux/macOS
lsof -i :3000

# Matar o processo e iniciar novamente
```

### ❌ "Porta 8000 já em uso"

```bash
# Windows
netstat -ano | findstr :8000

# Linux/macOS
lsof -i :8000
```

### ❌ "ModuleNotFoundError: No module named 'fastapi'"

**Solução:**
```bash
cd backend
pip install fastapi uvicorn sqlalchemy psycopg2-binary
```

### ❌ "npm: comando não encontrado"

**Solução:**
- Instale Node.js 18+ em https://nodejs.org/
- Reinicie o Terminal/PowerShell

### ❌ "Cannot find module 'http'"

**Solução:**
```bash
cd /workspace/atendimento
npm install
```

---

## 📋 Checklist Final

Antes de começar a usar, verifique:

- ✅ Docker está rodando (se usar Docker)?
- ✅ Terminal 1 mostra "ready to accept connections"?
- ✅ Terminal 2 mostra "Uvicorn running on http://127.0.0.1:8000"?
- ✅ Terminal 3 mostra "App ATENDIMENTO rodando"?
- ✅ http://localhost:8000/health retorna `{"status": "healthy"}`?
- ✅ http://localhost:3000/api/webhook/health retorna `{"status": "ok"}`?

Se sim para todos, **está pronto!** 🚀

---

## 🎯 Próximos Passos

1. **Teste as Interfaces:**
   - Acesse http://localhost:3000/ para criar Ordens
   - Acesse http://localhost:8000/docs para ver a API

2. **Leia o Guia de Testes:**
   - Veja `TESTE_INTEGRACAO.md` para todos os testes disponíveis
   - Veja `GUIA_ACESSO_INTERFACES.md` para instruções detalhadas

3. **Comece a Usar:**
   - Crie clientes em http://localhost:8000
   - Crie Ordens de Serviço em http://localhost:3000
   - Adicione fotos, vídeos e senhas

---

## 📞 Suporte

Se tiver problemas:

1. Verifique se todos os pré-requisitos estão instalados
2. Leia a seção "Troubleshooting" acima
3. Consulte os logs dos terminais
4. Verifique se as portas (3000, 8000, 5432) estão livres

**Bom desenvolvimento!** 🚀
