#!/bin/bash

# 🚀 Script para iniciar a aplicação completa (Linux/macOS)
# Uso: ./START.sh

set -e

echo "=============================================="
echo "  🚀 Sistema Híbrido FastAPI + Node.js"
echo "=============================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar pré-requisitos
echo -e "${YELLOW}📋 Verificando pré-requisitos...${NC}"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado${NC}"
    echo "Instale em: https://www.python.org/downloads/"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 encontrado$(python3 --version)${NC}"

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js não encontrado${NC}"
    echo "Instale em: https://nodejs.org/"
    exit 1
fi
echo -e "${GREEN}✅ Node.js encontrado: $(node --version)${NC}"

# Verificar Docker (opcional)
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker encontrado${NC}"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Docker não encontrado (PostgreSQL local será necessário)${NC}"
    DOCKER_AVAILABLE=false
fi

echo ""
echo -e "${YELLOW}📦 Instalando dependências...${NC}"

# Instalar dependências do Backend
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}📦 Criando ambiente virtual Python...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt 2>/dev/null || pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-multipart requests email-validator
    cd ..
    echo -e "${GREEN}✅ Backend pronto${NC}"
else
    echo -e "${GREEN}✅ Backend já instalado${NC}"
fi

# Instalar dependências do Node.js
if [ ! -d "atendimento/node_modules" ] && [ -d "atendimento" ]; then
    echo -e "${YELLOW}📦 Instalando dependências Node.js...${NC}"
    cd atendimento
    npm install
    cd ..
    echo -e "${GREEN}✅ Node.js pronto${NC}"
elif [ -d "atendimento" ]; then
    echo -e "${GREEN}✅ Node.js já instalado${NC}"
fi

echo ""
echo -e "${YELLOW}🚀 Iniciando serviços...${NC}"
echo ""

# Iniciar Docker se disponível
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo -e "${YELLOW}🐘 Iniciando PostgreSQL com Docker...${NC}"
    docker-compose up -d postgres pgadmin
    echo -e "${GREEN}✅ PostgreSQL rodando em localhost:5432${NC}"
    echo -e "${GREEN}✅ pgAdmin rodando em http://localhost:5050${NC}"
    sleep 3
fi

echo ""
echo -e "${YELLOW}⚠️  VOCÊ PRECISA ABRIR 2 NOVOS TERMINAIS PARA INICIAR OS SERVIDORES${NC}"
echo ""
echo -e "${YELLOW}📋 Terminal 2 - FastAPI Backend:${NC}"
echo -e "${GREEN}cd backend && source venv/bin/activate && python main.py${NC}"
echo ""
echo -e "${YELLOW}📋 Terminal 3 - Node.js Atendimento:${NC}"
echo -e "${GREEN}cd atendimento && node server/index.js${NC}"
echo ""
echo -e "${YELLOW}🌐 URLs de Acesso:${NC}"
echo -e "  ${GREEN}FastAPI:${NC} http://localhost:8000"
echo -e "  ${GREEN}Docs:${NC} http://localhost:8000/docs"
echo -e "  ${GREEN}Node.js:${NC} http://localhost:3000"
echo -e "  ${GREEN}pgAdmin:${NC} http://localhost:5050"
echo ""
echo -e "${GREEN}🎉 Preparação concluída!${NC}"
echo ""
