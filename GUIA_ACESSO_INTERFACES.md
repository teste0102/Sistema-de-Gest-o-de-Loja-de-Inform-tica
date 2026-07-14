# 🌐 GUIA DE ACESSO ÀS INTERFACES

## 🚀 URLs de Acesso

### **FastAPI (Gestão + Webhooks)**
```
http://localhost:8000
http://localhost:8000/docs          (Documentação Swagger)
http://localhost:8000/openapi.json  (Schema OpenAPI)
```

### **Node.js (Atendimento - Ordem de Serviço)**
```
http://localhost:3000               (Interface Principal)
http://localhost:3000/cliente.html  (Modo Cliente - Tablet)
http://localhost:3000/config.html   (Configurações)
http://localhost:3000/os.html       (Lista de Ordens)
http://localhost:3000/editar-os.html (Editar OS)
http://localhost:3000/sessoes.html  (Gerenciar Sessões)
```

---

## 📱 COMO USAR

### 1️⃣ **Acessar a Interface do Atendimento**

Abra no navegador:
```
http://localhost:3000/
```

**Você verá:**
- Header com "Ordem de Serviço"
- Status do servidor
- Botão para modo cliente/configurações
- Formulário para criar/editar OS
- Área para desenho de senha
- Upload de fotos e vídeos

### 2️⃣ **Criar uma Nova OS**

1. Na interface principal (http://localhost:3000/)
2. Preencha:
   - Cliente
   - Modelo do telefone
   - Problema
   - Senha (opcional)
3. Clique em "Criar OS"

### 3️⃣ **Adicionar Senha (Padrão de Desenho)**

Na tela de edição:
1. Clique em "Desenhar Padrão"
2. Faça o desenho ligando os 9 pontos
3. A senha é salva automaticamente

### 4️⃣ **Upload de Fotos**

1. Clique em "Adicionar Foto"
2. Tire uma foto da câmera OU faça upload
3. Foto é salva e vinculada à OS

### 5️⃣ **Upload de Vídeos**

1. Clique em "Gravar Vídeo"
2. Grave o processo de atendimento
3. Vídeo é salvo e vinculado à OS

---

## 🔗 **FLUXO INTEGRADO**

```
Você acessa http://localhost:3000/
          ↓
Cria/Edita OS no Node.js
          ↓
Node.js AUTOMATICAMENTE notifica FastAPI via webhook
          ↓
FastAPI atualiza banco PostgreSQL
          ↓
Dados sincronizados em tempo real!
```

---

## 📊 **Verifying Data in FastAPI**

Você pode verificar os dados salvos via API FastAPI:

### **Ver todas as Ordens**
```bash
curl http://localhost:8000/api/ordens/
```

### **Ver uma Ordem Específica**
```bash
curl http://localhost:8000/api/ordens/1
```

### **Ver todos os Clientes**
```bash
curl http://localhost:8000/api/clientes/
```

### **Ver Documentação Interativa**
Abra no navegador:
```
http://localhost:8000/docs
```

Você pode fazer requisições direto da documentação!

---

## 🎯 **Próximos Passos**

Agora que você tem:
- ✅ Node.js rodando em http://localhost:3000
- ✅ FastAPI rodando em http://localhost:8000
- ✅ Webhooks funcionando
- ✅ Banco PostgreSQL conectado

Você pode:

1. **Testar Manualmente a Interface**
   - Criar OS em http://localhost:3000
   - Ver dados em http://localhost:8000/docs

2. **Implementar Frontend Unificado**
   - Integrar ambos em uma única interface React

3. **Implementar Sincronização com Servidor Remoto**
   - Sincronizar dados com outro servidor

4. **Implementar WhatsApp**
   - Enviar notificações por WhatsApp

---

## ⚡ **ATALHOS ÚTEIS**

### **Reiniciar FastAPI**
```bash
pkill -f "uvicorn main:app"
python -m uvicorn main:app --host 127.0.0.1 --port 8000 &
```

### **Reiniciar Node.js**
```bash
pkill -f "node server/index.js"
cd /workspace/atendimento
node server/index.js &
```

### **Ver Logs FastAPI**
```bash
tail -f /tmp/fastapi.log
```

### **Ver Logs Node.js**
```bash
tail -f /tmp/nodejs.log
```

### **Testar Webhook**
```bash
curl -X POST http://localhost:8000/api/webhook/ordem/senha \
  -H "Content-Type: application/json" \
  -d '{"numeroOS": 1, "senhaID": "teste", "tipoSenha": "padrao"}'
```

---

## 🆘 **Troubleshooting**

### **Node.js não abre em http://localhost:3000**
```bash
# Verificar se Node.js está rodando
ps aux | grep "node server"

# Se não estiver, reiniciar:
cd /workspace/atendimento
node server/index.js &
```

### **FastAPI não responde**
```bash
# Verificar se está rodando
ps aux | grep "uvicorn"

# Se não, reiniciar do diretório correto:
cd /home/user/Sistema-de-Gest-o-de-Loja-de-Inform-tica/backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 &
```

### **Porta já está em uso**
```bash
# FastAPI (8000)
lsof -i :8000
kill -9 <PID>

# Node.js (3000)
lsof -i :3000
kill -9 <PID>
```

---

## 📞 **Resumo**

| Componente | URL | Status | Função |
|---|---|---|---|
| Node.js | http://localhost:3000 | ✅ Rodando | Interface de Atendimento |
| FastAPI | http://localhost:8000 | ✅ Rodando | API + Webhooks |
| PostgreSQL | localhost:5432 | ✅ Rodando | Banco de Dados |
| Documentação | http://localhost:8000/docs | ✅ Acessível | Swagger UI |

Tudo pronto! Você pode começar a testar agora! 🚀
