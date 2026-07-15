# 🖥️ FAZER PULL E SUBIR NA SUA MÁQUINA WINDOWS

## 📥 PASSO 1: Fazer Pull do Código

### Opção A: Se você já tem o repositório clonado

**1. Abra PowerShell como Administrador**

**2. Navegue até a pasta do projeto:**
```powershell
cd "C:\caminho\para\Sistema-de-Gest-o-de-Loja-de-Inform-tica"
```

**3. Faça pull da branch:**
```powershell
git fetch origin claude/multi-server-db-sync-1hx0l2
git checkout claude/multi-server-db-sync-1hx0l2
git pull origin claude/multi-server-db-sync-1hx0l2
```

### Opção B: Se você NÃO tem o repositório clonado

**1. Crie uma pasta para o projeto:**
```powershell
mkdir "C:\projetos"
cd "C:\projetos"
```

**2. Clone o repositório:**
```powershell
git clone http://127.0.0.1:41729/git/teste0102/Sistema-de-Gest-o-de-Loja-de-Inform-tica.git
cd Sistema-de-Gest-o-de-Loja-de-Inform-tica
```

**3. Checkout da branch:**
```powershell
git checkout claude/multi-server-db-sync-1hx0l2
```

---

## ⚙️ PASSO 2: Verificar Pré-requisitos

Abra PowerShell e execute:

```powershell
# Verificar Docker
docker --version

# Verificar Docker Compose
docker compose version

# Verificar Git
git --version
```

Todos devem retornar versão. Se algum não existir, instale:
- **Docker Desktop:** https://www.docker.com/products/docker-desktop
- **Git:** https://git-scm.com/download/win

---

## 🚀 PASSO 3: Executar Inicialização

### Opção A: AUTOMÁTICO (Recomendado)

```powershell
cd "C:\caminho\para\Sistema-de-Gest-o-de-Loja-de-Inform-tica"
.\INICIAR_SERVIDOR.bat
```

O script vai fazer tudo automaticamente! ✨

### Opção B: MANUAL (Passo a Passo)

```powershell
# 1. Navegar até a pasta
cd "C:\caminho\para\Sistema-de-Gest-o-de-Loja-de-Inform-tica"

# 2. Criar diretórios
mkdir data\fotos -Force
mkdir data\postgres -Force

# 3. Criar .env (se não existir)
if (-not (Test-Path .env)) {
    @"
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/loja_informatica
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=loja_informatica
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=sua-chave-secreta-super-segura-aqui
NODE_ENV=production
PORT=3000
"@ | Out-File .env
}

# 4. Iniciar Docker Compose
docker compose up -d

# 5. Aguardar 20 segundos
Start-Sleep -Seconds 20

# 6. Executar primeira migration
Write-Host "Executando migration 001..." -ForegroundColor Green
docker compose exec postgres psql -U postgres -d loja_informatica -f /dev/stdin < backend/migrations/001_criar_tabelas_os_completo.sql

# 7. Executar segunda migration
Write-Host "Executando migration 002..." -ForegroundColor Green
docker compose exec postgres psql -U postgres -d loja_informatica -f /dev/stdin < backend/migrations/002_adicionar_campos_essenciais_os.sql

Write-Host "✅ Servidor iniciado com sucesso!" -ForegroundColor Green
Write-Host "Acesse: http://localhost:8000/docs" -ForegroundColor Cyan
```

---

## ✅ VERIFICAR SE FUNCIONOU

### 1. Ver Logs
```powershell
docker compose logs -f backend
```

### 2. Testar via Browser
```
http://localhost:8000/docs
```

Você deve ver a **página Swagger com todos os endpoints**!

### 3. Ver Status dos Containers
```powershell
docker compose ps
```

Deve mostrar 4 containers:
- ✅ loja_postgres (PostgreSQL)
- ✅ loja_pgadmin (pgAdmin - gerenciador BD)
- ✅ loja_backend (FastAPI)
- ✅ loja_frontend (Node.js/React)

---

## 🧪 TESTAR ENDPOINTS

### Via Swagger (Recomendado)
1. Abra http://localhost:8000/docs
2. Clique em qualquer endpoint
3. Clique em "Try it out"
4. Preencha os parâmetros
5. Clique "Execute"

### Via PowerShell (Manual)

**Gerar novo número OS:**
```powershell
curl -X POST "http://localhost:8000/api/os/gerar-numero?cliente_id=1"
```

**Obter tipos de dano:**
```powershell
curl "http://localhost:8000/api/recursos/tipos-dano"
```

**Ver status de sync:**
```powershell
curl "http://localhost:8000/api/sync/status"
```

---

## 🛑 PARAR SERVIDOR

```powershell
docker compose down
```

Para limpar tudo (INCLUDING dados):
```powershell
docker compose down -v
```

---

## 📊 SERVIÇOS DISPONÍVEIS

| Serviço | URL | Credenciais |
|---------|-----|------------|
| **FastAPI** | http://localhost:8000 | - |
| **Swagger Docs** | http://localhost:8000/docs | - |
| **PostgreSQL** | localhost:5432 | user: postgres, pass: postgres |
| **pgAdmin** | http://localhost:5050 | user: admin@loja.com, pass: admin |

---

## 🆘 TROUBLESHOOTING

### ❌ "Docker daemon is not running"
**Solução:** Abra Docker Desktop (procure no Menu Iniciar)

### ❌ "Port 5432 already in use"
**Solução:** 
```powershell
docker compose down
docker system prune -a
docker compose up -d
```

### ❌ "Cannot connect to database"
**Solução:** Aguarde mais tempo (30-60 segundos). PostgreSQL leva tempo para iniciar.
```powershell
docker compose logs postgres
```

### ❌ Migrations falhando
**Solução:** Verificar se banco está pronto:
```powershell
docker compose exec -T postgres pg_isready -U postgres
```

Se retornar "accepting connections", banco está pronto. Se não, aguarde mais.

---

## 📝 RESUMO DO FLUXO

```
1. ✅ Fazer pull do código
2. ✅ Instalar Docker Desktop (se não tiver)
3. ✅ Executar INICIAR_SERVIDOR.bat
4. ✅ Aguardar ~30 segundos
5. ✅ Abrir http://localhost:8000/docs
6. ✅ Testar endpoints
7. 🎉 Sistema rodando!
```

---

## 🎉 PARABÉNS!

Você tem um sistema completo de OS com:
- ✅ 28 endpoints FastAPI
- ✅ Banco de dados PostgreSQL
- ✅ Criptografia RSA-2048
- ✅ Sincronização offline-first
- ✅ Gerenciamento de fotos
- ✅ Laudos técnicos

**Próxima fase:** React components para captura/visualização!

---

## 💡 DICAS

- Mantenha Docker Desktop aberto enquanto estiver desenvolvendo
- Veja os logs com: `docker compose logs -f`
- Reinicie com: `docker compose restart`
- Não feche o PowerShell enquanto estiver vendo logs
