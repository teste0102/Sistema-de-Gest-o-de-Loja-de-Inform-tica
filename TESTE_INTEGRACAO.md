# 🧪 TESTE DE INTEGRAÇÃO: FastAPI + Node.js

## 📋 Pré-Requisitos

- [x] Python 3.8+
- [x] Node.js 14+
- [x] PostgreSQL rodando
- [x] Arquivos criados (webhook.py, webhook.js, sync_service.py)

---

## 🚀 PASSO 1: Preparar Banco de Dados

```bash
# Abra o terminal na pasta do projeto

cd /home/user/Sistema-de-Gest-o-de-Loja-de-Inform-tica

# Faça as migrations (criar novas tabelas)
python -m alembic upgrade head

# Ou, se não tiver alembic, delete e recrie o banco:
rm loja_informatica.db  # (se usar SQLite)
# PostgreSQL: DELETE FROM * (manual)
```

---

## 🚀 PASSO 2: Iniciar FastAPI

```bash
# Terminal 1 - FastAPI

cd /home/user/Sistema-de-Gest-o-de-Loja-de-Inform-tica/backend

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Você verá:
# ✅ Uvicorn running on http://0.0.0.0:8000
```

---

## 🚀 PASSO 3: Iniciar Node.js

```bash
# Terminal 2 - Node.js

cd /workspace/atendimento

node server/index.js

# Você verá:
# ✅ App ATENDIMENTO (Ordem de Servico) rodando
#    Neste PC:   http://localhost:3000
```

---

## 🧪 TESTE 1: Health Check

Verificar se ambos os servidores estão online:

```bash
# FastAPI
curl http://localhost:8000/health

# Resposta esperada:
{
  "status": "healthy",
  "database": "ok",
  "system": "Linux"
}

# Node.js
curl http://localhost:3000/api/webhook/health

# Resposta esperada:
{
  "status": "ok",
  "servidor": "atendimento-node",
  "webhooks": ["ordem/senha-salva", "ordem/foto-salva", "ordem/video-salvo", "sync/completa"]
}
```

---

## 🧪 TESTE 2: Criar Cliente

```bash
# FastAPI: POST /api/clientes

curl -X POST http://localhost:8000/api/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": 1,
    "nome": "João Silva",
    "telefone": "11999999999",
    "email": "joao@example.com"
  }'

# Resposta esperada:
{
  "id": 1,
  "codigo": 1,
  "nome": "João Silva",
  "created_at": "2024-07-14T...",
  "updated_at": "2024-07-14T..."
}
```

---

## 🧪 TESTE 3: Criar Ordem de Serviço

```bash
# FastAPI: POST /api/ordens

curl -X POST http://localhost:8000/api/ordens \
  -H "Content-Type: application/json" \
  -d '{
    "numero": 1,
    "cliente_id": 1,
    "descricao": "Trocar bateria",
    "data_abertura": "2024-07-14",
    "status": "aberto",
    "tecnico": "Carlos"
  }'

# Resposta esperada:
{
  "id": 1,
  "numero": 1,
  "cliente_id": 1,
  "descricao": "Trocar bateria",
  "fotos": null,
  "videos": null,
  "created_at": "2024-07-14T..."
}
```

---

## 🧪 TESTE 4: Webhook - Adicionando Senha

```bash
# Node.js notifica FastAPI que senha foi salva

curl -X POST http://localhost:8000/api/webhook/ordem/senha \
  -H "Content-Type: application/json" \
  -d '{
    "numeroOS": 1,
    "senhaID": "pwd-abc123",
    "tipoSenha": "padrao"
  }'

# Resposta esperada:
{
  "ok": true,
  "message": "Senha da OS 1 sincronizada"
}

# Verificar se atualizou:
curl http://localhost:8000/api/ordens/1

# Deve ter:
"node_senha_id": "pwd-abc123",
"senha_tipo": "padrao"
```

---

## 🧪 TESTE 5: Webhook - Adicionando Foto

```bash
# Node.js notifica FastAPI que foto foi salva

curl -X POST http://localhost:8000/api/webhook/ordem/foto \
  -H "Content-Type: application/json" \
  -d '{
    "numeroOS": 1,
    "fotoID": "foto-001",
    "url": "http://localhost:3000/uploads/os-1/foto-001.jpg",
    "descricao": "Frente do telefone"
  }'

# Resposta esperada:
{
  "ok": true,
  "message": "Foto foto-001 sincronizada à OS 1"
}

# Verificar se atualizou:
curl http://localhost:8000/api/ordens/1

# Deve ter:
"fotos": [
  {
    "id": "foto-001",
    "url": "http://localhost:3000/uploads/os-1/foto-001.jpg",
    "descricao": "Frente do telefone",
    "data": "2024-07-14T..."
  }
]
```

---

## 🧪 TESTE 6: Webhook - Adicionando Vídeo

```bash
# Node.js notifica FastAPI que vídeo foi salvo

curl -X POST http://localhost:8000/api/webhook/ordem/video \
  -H "Content-Type: application/json" \
  -d '{
    "numeroOS": 1,
    "videoID": "video-001",
    "url": "http://localhost:3000/uploads/os-1/video-001.mp4",
    "duracao": 125,
    "descricao": "Diagnóstico"
  }'

# Resposta esperada:
{
  "ok": true,
  "message": "Vídeo video-001 sincronizado à OS 1"
}

# Verificar se atualizou:
curl http://localhost:8000/api/ordens/1

# Deve ter:
"videos": [
  {
    "id": "video-001",
    "url": "http://localhost:3000/uploads/os-1/video-001.mp4",
    "duracao": 125,
    "descricao": "Diagnóstico",
    "data": "2024-07-14T..."
  }
]
```

---

## ✅ RESULTADO ESPERADO DOS TESTES

Se todos passarem:

1. ✅ FastAPI recebe criação de cliente
2. ✅ FastAPI recebe criação de ordem
3. ✅ FastAPI recebe notificações de webhook
4. ✅ Ordem atualiza com informações do Node.js
5. ✅ Fotos, vídeos e senhas ficam linkadas à ordem

---

## 📊 Verificação Final

Após todos os testes, consulte a ordem:

```bash
curl http://localhost:8000/api/ordens/1 | jq .
```

Deve mostrar:
```json
{
  "id": 1,
  "numero": 1,
  "cliente_id": 1,
  "descricao": "Trocar bateria",
  "status": "aberto",
  "tecnico": "Carlos",
  "node_os_id": null,
  "node_senha_id": "pwd-abc123",
  "senha_tipo": "padrao",
  "fotos": [
    {
      "id": "foto-001",
      "url": "http://localhost:3000/uploads/os-1/foto-001.jpg",
      "descricao": "Frente do telefone",
      "data": "2024-07-14T15:30:00"
    }
  ],
  "videos": [
    {
      "id": "video-001",
      "url": "http://localhost:3000/uploads/os-1/video-001.mp4",
      "duracao": 125,
      "descricao": "Diagnóstico",
      "data": "2024-07-14T15:30:00"
    }
  ],
  "created_at": "2024-07-14T15:20:00",
  "updated_at": "2024-07-14T15:30:00"
}
```

---

## 🆘 Troubleshooting

### FastAPI não inicia
```bash
# Checar se porta 8000 está livre
lsof -i :8000

# Checar se PostgreSQL está rodando
psql -U postgres -h localhost -d loja_informatica -c "SELECT 1"
```

### Node.js não inicia
```bash
# Checar se porta 3000 está livre
lsof -i :3000

# Reinstalar dependências
npm install
```

### Webhook não funciona
```bash
# Verificar logs do FastAPI
# - Ver se request chegou
# - Ver se atualizou banco

# Verificar logs do Node.js
# - Ver se webhook foi chamado
```

---

## 🎯 Próximos Passos

Se tudo passou ✅:

1. **Criar Frontend** que integra ambos os APIs
2. **Implementar Sincronização com Servidor Remoto**
3. **Adicionar Suporte a WhatsApp**
4. **Deploy em Produção**

Qual quer que eu implemente agora? 🚀
