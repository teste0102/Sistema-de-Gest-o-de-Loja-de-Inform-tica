# 🔄 Scripts de Reinicialização de Servidor

## ✅ SIM! É necessário reiniciar o servidor quando atualizar código

Ao atualizar o código (Python backend ou React frontend), é necessário **reiniciar os containers Docker** para que as mudanças sejam carregadas.

---

## 📁 Arquivos Disponíveis

### 1. **REINICIAR_SERVIDOR.ps1** (Recomendado para Windows)
- **Melhor opção** para Windows 10/11
- Cores formatadas no console
- Pergunta se deseja abrir o navegador
- Execute: `.\REINICIAR_SERVIDOR.ps1`

**Primeira vez (se der erro de permissão):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. **REINICIAR_SERVIDOR.bat** (Compatível com Windows)
- Funciona em qualquer versão do Windows
- Execute: `REINICIAR_SERVIDOR.bat`
- Clique duplo no arquivo

### 3. **REINICIAR_SERVIDOR.sh** (Para Linux/Mac)
- Execute: `chmod +x REINICIAR_SERVIDOR.sh`
- Depois: `./REINICIAR_SERVIDOR.sh`

---

## 🚀 Como Usar

### **Opção 1: Duplo clique (Mais Fácil)**
1. Vá à área de trabalho
2. Duplo clique em `REINICIAR_SERVIDOR.bat`
3. Pronto! Vai reiniciar tudo

### **Opção 2: PowerShell (Mais Moderno)**
1. Clique direito em `REINICIAR_SERVIDOR.ps1`
2. Selecione "Executar com PowerShell"
3. Pressione `S` para abrir navegador automaticamente

### **Opção 3: Terminal/Cmd**
```bash
# Windows CMD
cd Desktop
REINICIAR_SERVIDOR.bat

# Windows PowerShell
.\REINICIAR_SERVIDOR.ps1

# Linux/Mac
./REINICIAR_SERVIDOR.sh
```

---

## ⏱️ Quando Reiniciar?

### ✅ **SEMPRE reinicie quando:**
- Modificar arquivos Python (backend)
- Modificar componentes React (frontend)
- Adicionar novas rotas ou endpoints
- Atualizar dependências (requirements.txt, package.json)
- Alterar variáveis de ambiente (.env)

### ❌ **NÃO precisa reiniciar quando:**
- Apenas visualizar/ler dados (GET requests)
- Mudar só CSS (se fez reload da página)
- Verificar status do banco (já está rodando)

---

## 📊 O Que Acontece ao Reiniciar?

1. **Para os containers:**
   - ⏹️ Backend (FastAPI) para
   - ⏹️ Frontend (React) para
   - ⏹️ PostgreSQL para
   - ⏹️ PgAdmin para

2. **Aguarda 2 segundos**

3. **Inicia tudo novamente:**
   - 🚀 PostgreSQL conecta
   - 🚀 Backend inicia na porta 8000
   - 🚀 Frontend inicia na porta 3000
   - 🚀 PgAdmin inicia na porta 5050

4. **Aguarda 10 segundos**
   - Tempo para tudo ficar pronto

5. **Mostra status:**
   ```
   CONTAINER ID   IMAGE                   STATUS
   abc123         postgres:16-alpine      Up 5 seconds
   def456         backend:latest          Up 3 seconds
   ghi789         frontend:latest         Up 2 seconds
   ```

---

## 🔗 URLs Depois de Reiniciar

Após reiniciar com sucesso, acesse:

| Serviço | URL | Uso |
|---------|-----|-----|
| **Frontend** | http://localhost:3000 | Interface do Sistema |
| **Backend API** | http://localhost:8000 | Endpoints da API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **PgAdmin** | http://localhost:5050 | Gerenciar Banco de Dados |

---

## ⚠️ Problemas Comuns

### ❌ "Docker não encontrado"
**Solução:**
- Instale Docker Desktop: https://www.docker.com/products/docker-desktop
- Reinicie o computador após instalar

### ❌ "Porta 3000 já está em uso"
**Solução:**
```powershell
# Windows - Liberar porta 3000
netstat -ano | findstr :3000
taskkill /PID <PID_NUMBER> /F
```

### ❌ "Porta 8000 já está em uso"
**Solução:**
```powershell
# Windows - Liberar porta 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

### ❌ Containers param rapidamente (erro ao iniciar)
**Solução:**
1. Abra o arquivo `/docker-compose.yml`
2. Verifique se está na pasta correta
3. Execute: `docker compose logs` para ver erros
4. Verifique `.env` se existir

---

## 📝 Checklist Antes de Reiniciar

- ✅ Arquivo `.env` configurado (se necessário)
- ✅ Docker Desktop está aberto/rodando
- ✅ Nenhuma outra aplicação na porta 3000/8000
- ✅ Mudanças de código foram salvas (Ctrl+S)
- ✅ Git commit foi feito (se usando versionamento)

---

## 🔍 Verificar Status Sem Reiniciar

Se quiser apenas **verificar se está rodando**:

```powershell
docker compose ps
```

Saída esperada (tudo "Up"):
```
STATUS
Up 2 hours
Up 2 hours
Up 2 hours
Up 2 hours
```

---

## 🛠️ Comandos Úteis

```powershell
# Ver logs do backend
docker compose logs backend

# Ver logs do frontend
docker compose logs frontend

# Ver logs do postgres
docker compose logs postgres

# Parar tudo (sem deletar dados)
docker compose down

# Iniciar tudo
docker compose up -d

# Deletar tudo (CUIDADO! Perde dados)
docker compose down -v
```

---

## ✨ Dica Profissional

**Deixe um PowerShell aberto mostrando logs:**

```powershell
docker compose logs -f
```

Assim você vê em tempo real quando cada serviço inicia/falha.

---

## 📞 Resumo Rápido

| Ação | Comando |
|------|---------|
| Reiniciar (Fácil) | Duplo clique `REINICIAR_SERVIDOR.bat` |
| Reiniciar (Moderno) | `.\REINICIAR_SERVIDOR.ps1` |
| Ver status | `docker compose ps` |
| Ver logs | `docker compose logs -f` |
| Liberar porta | `netstat -ano \| findstr :PORTA` |

---

**Último Update:** 2026-07-16
**Status:** ✅ Pronto para Uso
