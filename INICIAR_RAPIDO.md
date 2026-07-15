# 🚀 Guia Rápido de Inicialização

## Windows (Recomendado para você)

### Opção 1: Script Automático (Mais Fácil)
```bash
# Execute o script de inicialização
INICIAR_SERVIDOR.bat
```

O script vai automaticamente:
- ✅ Verificar Docker
- ✅ Criar arquivo `.env`
- ✅ Iniciar Docker Compose
- ✅ Executar migrations SQL
- ✅ Validar servidor

### Opção 2: Manual (Passo a Passo)

**1. Abrir PowerShell como Administrador**

**2. Criar arquivo `.env`:**
```powershell
@"
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/loja_informatica
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=loja_informatica
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=sua-chave-secreta-super-segura-aqui
"@ | Out-File -Encoding UTF8 .env
```

**3. Criar diretórios:**
```powershell
mkdir data/fotos -Force
mkdir data/postgres -Force
```

**4. Iniciar Docker Compose:**
```powershell
docker-compose up -d
```

**5. Aguardar 10 segundos e executar migrations:**
```powershell
docker-compose exec -T postgres psql -U postgres -d loja_informatica -f /dev/stdin < backend/migrations/001_criar_tabelas_os_completo.sql
docker-compose exec -T postgres psql -U postgres -d loja_informatica -f /dev/stdin < backend/migrations/002_adicionar_campos_essenciais_os.sql
```

---

## Linux/Mac

```bash
# Tornar script executável
chmod +x INICIAR_SERVIDOR.sh

# Executar
./INICIAR_SERVIDOR.sh
```

---

## ✅ Verificar Saúde

Após inicializar, verifique se tudo está funcionando:

### 1. Abrir Swagger (Interface de testes)
```
http://localhost:8000/docs
```

### 2. Testar Endpoints Básicos
```bash
# Gerar novo número OS
curl -X POST "http://localhost:8000/api/os/gerar-numero?cliente_id=1"

# Obter status de sync
curl "http://localhost:8000/api/sync/status"

# Listar tipos de dano
curl "http://localhost:8000/api/recursos/tipos-dano"
```

### 3. Ver Logs
```bash
docker-compose logs -f backend
```

---

## 🛑 Parar Servidor

```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (CUIDADO - remove dados!)
docker-compose down -v
```

---

## 📊 Serviços Disponíveis

| Serviço | URL | Usuário | Senha |
|---------|-----|---------|-------|
| **FastAPI** | http://localhost:8000 | - | - |
| **Swagger Docs** | http://localhost:8000/docs | - | - |
| **PostgreSQL** | localhost:5432 | postgres | postgres |
| **pgAdmin** | http://localhost:5050 | admin@example.com | admin |

---

## 🔧 Troubleshooting

### Problema: "Docker daemon is not running"
**Solução:** Abra o Docker Desktop

### Problema: "Port 5432 already in use"
**Solução:** 
```bash
# Parar containers antigos
docker-compose down

# Ou mude a porta em docker-compose.yml
```

### Problema: "Database does not exist"
**Solução:** 
```bash
# Aguarde 20 segundos após iniciar (banco está sendo criado)
docker-compose logs postgres
```

### Problema: Migrations falhando
**Solução:**
```bash
# Verificar se banco está pronto
docker-compose exec -T postgres pg_isready -U postgres

# Ver logs do banco
docker-compose logs postgres
```

---

## 📝 Próximos Passos

✅ Servidor iniciado com sucesso!

**Para testar os endpoints:**
1. Acesse http://localhost:8000/docs
2. Clique em "Try it out" para qualquer endpoint
3. Preencha os parâmetros e veja a resposta

**Exemplos de fluxo:**
```
1. POST /api/os/gerar-numero → Cria nova OS
2. POST /api/os/{id}/senhas → Define senha (PIN/Padrão)
3. POST /api/os/{id}/fotos/upload → Upload de foto
4. POST /api/os/{id}/laudo → Cria laudo técnico
5. POST /api/sync/enfileirar → Enfileira para sincronizar
```

---

## 🆘 Suporte

Se tiver problemas:
1. Verifique se Docker está rodando
2. Execute: `docker-compose logs backend`
3. Verifique arquivo `.env`
4. Tente: `docker-compose restart`
