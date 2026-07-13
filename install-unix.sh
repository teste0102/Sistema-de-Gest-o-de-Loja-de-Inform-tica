#!/bin/bash

# ===== INSTALLER PARA LINUX/MACOS =====
# Sistema de Gestão de Loja de Informática

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

clear

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Sistema de Gestão de Loja de Informática - Installer     ║"
echo "║                 Linux/macOS Version                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# ===== VERIFICAÇÕES =====

echo -e "${YELLOW}[1/5]${NC} Verificando Python 3.11+..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗${NC} Python não encontrado!"
    echo "Instale em: https://www.python.org/"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python detectado"
python3 --version

echo ""
echo -e "${YELLOW}[2/5]${NC} Verificando Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗${NC} Node.js não encontrado!"
    echo "Instale em: https://nodejs.org/"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js detectado"
node --version
npm --version

# ===== BACKEND =====

echo ""
echo -e "${YELLOW}[3/5]${NC} Instalando Backend (FastAPI)..."
cd backend

if [ ! -d "venv" ]; then
    echo "  Criando ambiente virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "  Instalando dependências..."
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ⚠ Arquivo .env criado. Revise as configurações se necessário."
fi

echo -e "${GREEN}✓${NC} Backend instalado com sucesso"
cd ..

# ===== FRONTEND =====

echo ""
echo -e "${YELLOW}[4/5]${NC} Instalando Frontend (React)..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "  Instalando pacotes npm (pode levar alguns minutos)..."
    npm install -q
fi

if [ ! -f ".env.local" ]; then
    cp .env.example .env.local
    echo "  ⚠ Arquivo .env.local criado"
fi

echo -e "${GREEN}✓${NC} Frontend instalado com sucesso"
cd ..

# ===== RESUMO FINAL =====

echo ""
echo -e "${YELLOW}[5/5]${NC} Resumo da Instalação"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✓${NC} Backend: FastAPI + SQLAlchemy pronto"
echo -e "${GREEN}✓${NC} Frontend: React + Bootstrap pronto"
echo -e "${GREEN}✓${NC} Ambiente virtual criado"
echo -e "${GREEN}✓${NC} Pacotes npm instalados"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}🚀 PRÓXIMOS PASSOS:${NC}"
echo ""
echo "Abra 3 terminais diferentes:"
echo ""
echo -e "${YELLOW}Terminal 1 - Banco de Dados:${NC}"
echo "  docker-compose up postgres pgadmin"
echo ""
echo -e "${YELLOW}Terminal 2 - Backend:${NC}"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo -e "${YELLOW}Terminal 3 - Frontend:${NC}"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}🌐 Acessos:${NC}"
echo "  • Backend API:  http://localhost:8000"
echo "  • Swagger:      http://localhost:8000/docs"
echo "  • Frontend:     http://localhost:3000"
echo "  • pgAdmin:      http://localhost:5050"
echo ""
echo -e "${BLUE}📚 Veja INSTALACAO.md para mais detalhes${NC}"
echo ""
