# 🚀 COMECE AQUI - Guia Rápido

**ANTES, você DEVE ter instalado no seu PC:**

- ✅ **Python 3.11+** → https://www.python.org/downloads/
- ✅ **Node.js 18+** → https://nodejs.org/
- ✅ **Docker** (recomendado) → https://www.docker.com/products/docker-desktop/

---

## 3️⃣ PASSOS SIMPLES

### Passo 1: Abra o Terminal na pasta do projeto

```bash
cd Sistema-de-Gest-o-de-Loja-de-Inform-tica
```

### Passo 2: Execute o script de inicialização

**Linux/macOS:**
```bash
chmod +x START.sh
./START.sh
```

**Windows:**
```cmd
START.bat
```

### Passo 3: Siga as instruções do script

O script vai:
1. ✅ Verificar Python, Node.js e Docker
2. ✅ Instalar dependências automáticamente
3. ✅ Iniciar PostgreSQL com Docker
4. ✅ Mostrar comandos para abrir 2 novos terminais

---

## 📖 O que fazer depois do script

Você verá uma mensagem com 2 comandos. Abra **2 NOVOS TERMINAIS** e copie-cole cada comando:

### Terminal 2 (FastAPI Backend):
```bash
cd backend
source venv/bin/activate          # No Windows: venv\Scripts\activate
python main.py
```

Resultado esperado:
```
✅ Uvicorn running on http://127.0.0.1:8000
```

### Terminal 3 (Node.js Atendimento):
```bash
cd atendimento
node server/index.js
```

Resultado esperado:
```
✅ App ATENDIMENTO rodando
   Neste PC: http://localhost:3000
```

---

## ✅ Verificar se está tudo funcionando

Abra seu navegador em:

| URL | Função |
|-----|--------|
| http://localhost:3000 | 📝 Criar Ordens de Serviço |
| http://localhost:8000/docs | 📚 Documentação da API |
| http://localhost:5050 | 🐘 pgAdmin (Banco de Dados) |

---

## 🧪 Primeiro Teste

Cole no Terminal/PowerShell:

```bash
curl -X POST http://localhost:8000/api/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": 1,
    "nome": "Teste",
    "telefone": "11999999999",
    "email": "teste@test.com"
  }'
```

Se retornar dados do cliente, **FUNCIONA!** ✅

---

## 🎯 Próximo Passo

Leia a documentação completa:
- **INSTALACAO_LOCAL.md** → Guia detalhado com troubleshooting
- **TESTE_INTEGRACAO.md** → Todos os testes disponíveis
- **GUIA_ACESSO_INTERFACES.md** → Como usar as interfaces

---

## 💡 Dica: Manter Tudo Rodando

Deixe os 3 terminais abertos:
- Terminal 1: Docker PostgreSQL (rode `docker-compose up postgres`)
- Terminal 2: FastAPI
- Terminal 3: Node.js

Cada terminal fica com "print" de eventos que ajuda no debug.

---

**Qualquer dúvida, veja INSTALACAO_LOCAL.md** 🚀
