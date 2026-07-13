# 🚀 INSTALAÇÃO RÁPIDA - Sistema de Gestão de Loja

**⏱️ Tempo total: 5-10 minutos**

---

## ✅ Pré-Requisitos

Você precisa ter instalado no seu computador:

- ✅ **Python 3.11+** - [Baixar](https://www.python.org/downloads/)
- ✅ **Node.js 18+** - [Baixar](https://nodejs.org/)
- ✅ **Git** - [Baixar](https://git-scm.com/download)
- ✅ **Docker Desktop** - [Baixar](https://www.docker.com/products/docker-desktop) (opcional, mas recomendado)

---

## 📥 PASSO 1: Clonar o Repositório

Abra o Terminal/PowerShell e execute:

```bash
git clone https://github.com/teste0102/Sistema-de-Gest-o-de-Loja-de-Inform-tica.git

cd Sistema-de-Gest-o-de-Loja-de-Inform-tica

git checkout claude/loja-informatica-setup-6rgvdu
```

---

## 🔧 PASSO 2: Instalação Automática

### **Windows** 🪟

Localize o arquivo `install-windows.bat` na pasta e **clique duas vezes** para executar.

Ou abra PowerShell na pasta e digite:
```powershell
.\install-windows.bat
```

### **Linux/macOS** 🐧 / 🍎

Abra o Terminal na pasta e execute:
```bash
chmod +x install-unix.sh
./install-unix.sh
```

---

## ✨ PASSO 3: Iniciar a Aplicação

Agora você precisa abrir **3 terminais diferentes**:

### Terminal 1️⃣ - Banco de Dados

```bash
docker-compose up -d postgres pgadmin
```

✓ PostgreSQL estará em: `localhost:5432`  
✓ pgAdmin estará em: `http://localhost:5050`

---

### Terminal 2️⃣ - Backend (Python/FastAPI)

**Windows:**
```cmd
cd backend
venv\Scripts\activate
python main.py
```

**Linux/macOS:**
```bash
cd backend
source venv/bin/activate
python main.py
```

✓ Backend estará em: `http://localhost:8000`  
✓ API Docs em: `http://localhost:8000/docs`

---

### Terminal 3️⃣ - Frontend (React)

```bash
cd frontend
npm start
```

✓ Frontend estará em: `http://localhost:3000`

---

## 🧪 PASSO 4: Testar a Instalação

Abra o navegador e acesse:

1. **Frontend (Web):** http://localhost:3000
   - Você verá o Dashboard com estatísticas

2. **API Swagger:** http://localhost:8000/docs
   - Documentação interativa de todos os endpoints

3. **Banco de Dados:** http://localhost:5050
   - pgAdmin para gerenciar PostgreSQL
   - Usuário: `admin@loja.com`
   - Senha: `admin`

---

## ✅ Primeiro Teste: Criar um Cliente

No Terminal ou PowerShell, execute:

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

Se retornar dados do cliente, **está funcionando!** ✅

---

## 🐛 Problemas Comuns?

### ❌ "Python não encontrado"
**Solução:** Instale Python 3.11+ em https://www.python.org/

### ❌ "Node.js não encontrado"
**Solução:** Instale Node.js em https://nodejs.org/

### ❌ "Connection refused: localhost:5432"
**Solução:** Certifique-se de que Docker está rodando e execute:
```bash
docker-compose up postgres
```

### ❌ "Porta 3000 já em uso"
**Solução:** Mude a porta com:
```bash
PORT=3001 npm start
```

### ❌ "Porta 8000 já em uso"
**Solução:** Mude a porta com:
```bash
python main.py --port 8001
```

---

## 📚 Próximos Passos

1. **Explore a API** em http://localhost:8000/docs
2. **Teste o Frontend** em http://localhost:3000
3. **Leia a documentação completa** em `INSTALACAO.md`
4. **Comece a desenvolver!**

---

## 🎯 Estrutura de Pastas

```
Sistema-de-Gest-o-de-Loja-de-Inform-tica/
├── backend/          # Python/FastAPI
│   ├── venv/         # Ambiente virtual (criado após instalação)
│   ├── main.py       # App principal
│   ├── requirements.txt
│   └── .env          # Configurações (criado após instalação)
│
├── frontend/         # React
│   ├── node_modules/ # Pacotes npm (criado após instalação)
│   ├── src/
│   ├── package.json
│   └── .env.local    # Configurações (criado após instalação)
│
├── docker-compose.yml # PostgreSQL + pgAdmin
├── install-windows.bat # Installer para Windows
├── install-unix.sh    # Installer para Linux/macOS
├── INSTALACAO.md      # Documentação completa
└── README.md          # Documentação principal
```

---

## 🔗 URLs Importantes

| Serviço | URL | Login |
|---------|-----|-------|
| **Frontend** | http://localhost:3000 | - |
| **API Backend** | http://localhost:8000 | - |
| **Swagger Docs** | http://localhost:8000/docs | - |
| **pgAdmin** | http://localhost:5050 | admin@loja.com / admin |

---

## 💾 Credenciais Padrão

**Banco de Dados:**
- Host: `localhost`
- Porta: `5432`
- Usuário: `loja`
- Senha: `senha123`
- Banco: `loja_informatica`

---

## ✨ Pronto!

Agora você tem um sistema completo de **gestão de loja** rodando no seu computador! 🎉

Para dúvidas, veja:
- `INSTALACAO.md` - Guia detalhado
- `VERIFICACAO_FINAL.md` - Checklist
- `README.md` - Documentação completa

**Bom desenvolvimento!** 🚀
