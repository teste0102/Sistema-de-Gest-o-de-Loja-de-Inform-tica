#!/bin/bash

echo "🚀 Iniciando Sistema de Gestão de Loja..."
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se Docker está instalado
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker detectado"
    
    # Iniciar PostgreSQL via Docker
    echo -e "${YELLOW}→${NC} Iniciando PostgreSQL em container..."
    docker-compose up -d postgres pgadmin
    sleep 5
    echo -e "${GREEN}✓${NC} PostgreSQL rodando em localhost:5432"
    echo -e "${GREEN}✓${NC} pgAdmin disponível em http://localhost:5050"
else
    echo -e "${YELLOW}⚠${NC} Docker não encontrado. Usando PostgreSQL local."
    echo -e "${YELLOW}⚠${NC} Certifique-se de que PostgreSQL está rodando!"
fi

echo ""

# Backend
echo -e "${YELLOW}→${NC} Iniciando Backend (FastAPI)..."
cd backend

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}→${NC} Criando ambiente virtual..."
    python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}→${NC} Instalando dependências..."
    pip install -q -r requirements.txt
fi

# Criar .env se não existir
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠${NC} Arquivo .env criado. Revise as configurações se necessário."
fi

echo -e "${GREEN}✓${NC} Backend pronto"
cd ..

echo ""

# Frontend
echo -e "${YELLOW}→${NC} Iniciando Frontend (React)..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}→${NC} Instalando dependências (pode levar alguns minutos)..."
    npm install -q
fi

# Criar .env.local se não existir
if [ ! -f ".env.local" ]; then
    cp .env.example .env.local
    echo -e "${YELLOW}⚠${NC} Arquivo .env.local criado"
fi

echo -e "${GREEN}✓${NC} Frontend pronto"
cd ..

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Tudo pronto! Iniciando serviços...${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""

# Abrir em tmux ou mesmo terminal
if command -v tmux &> /dev/null; then
    echo -e "${YELLOW}→${NC} Usando tmux para gerenciar processos..."
    
    tmux new-session -d -s loja -x 120 -y 40
    
    tmux send-keys -t loja:0 "cd backend && source venv/bin/activate && python main.py" Enter
    sleep 2
    
    tmux new-window -t loja:1 -n frontend
    tmux send-keys -t loja:1 "cd frontend && npm start" Enter
    
    echo ""
    echo -e "${GREEN}✓ Backend rodando em http://localhost:8000${NC}"
    echo -e "${GREEN}✓ Frontend rodando em http://localhost:3000${NC}"
    echo ""
    echo "Para gerenciar as sessões tmux:"
    echo "  tmux attach -t loja          # Conectar"
    echo "  tmux kill-session -t loja    # Encerrar"
else
    echo -e "${YELLOW}→${NC} Iniciando em dois terminais (abra dois terminais)..."
    echo ""
    echo "Terminal 1 - Backend:"
    echo "  cd backend && source venv/bin/activate && python main.py"
    echo ""
    echo "Terminal 2 - Frontend:"
    echo "  cd frontend && npm start"
    echo ""
    echo "Sistema disponível em:"
    echo "  - API: http://localhost:8000"
    echo "  - Web: http://localhost:3000"
    echo "  - Swagger: http://localhost:8000/docs"
    
    # Iniciar em background se tiver capacidade
    cd backend
    source venv/bin/activate
    python main.py &
    BACKEND_PID=$!
    cd ../frontend
    npm start &
    FRONTEND_PID=$!
    
    echo ""
    echo "Processos iniciados:"
    echo "  Backend PID: $BACKEND_PID"
    echo "  Frontend PID: $FRONTEND_PID"
fi
