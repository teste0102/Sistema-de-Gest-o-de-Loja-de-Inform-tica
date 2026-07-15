#!/bin/bash

################################################################################
# Script de Inicialização - Sistema de OS
# Executa migrations, valida ambiente e inicia servidor
################################################################################

set -e

echo "================================"
echo "🚀 INICIALIZANDO SERVIDOR OS"
echo "================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# 1. VERIFICAR DOCKER
# ============================================================================
echo -e "${BLUE}1. Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker não encontrado. Instale Docker primeiro.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker disponível${NC}"
echo ""

# ============================================================================
# 2. VERIFICAR ARQUIVO .env
# ============================================================================
echo -e "${BLUE}2. Verificando configurações (.env)...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado${NC}"
    echo "Criando arquivo .env padrão..."
    cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/loja_informatica
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=loja_informatica

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=sua-chave-secreta-super-segura-aqui-32-caracteres

# Node.js
NODE_ENV=production
PORT=3000

# Paths
DATA_PATH=/data
FOTOS_PATH=/data/fotos
EOF
    echo -e "${GREEN}✅ Arquivo .env criado${NC}"
else
    echo -e "${GREEN}✅ Arquivo .env encontrado${NC}"
fi
echo ""

# ============================================================================
# 3. CRIAR DIRETÓRIOS DE DADOS
# ============================================================================
echo -e "${BLUE}3. Criando diretórios de dados...${NC}"
mkdir -p data/fotos
mkdir -p data/postgres
chmod 777 data
echo -e "${GREEN}✅ Diretórios criados${NC}"
echo ""

# ============================================================================
# 4. INICIAR DOCKER COMPOSE
# ============================================================================
echo -e "${BLUE}4. Iniciando serviços Docker...${NC}"
docker-compose up -d

echo "Aguardando serviços iniciarem..."
sleep 10

# Verificar se PostgreSQL está respondendo
echo "Verificando PostgreSQL..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U postgres &> /dev/null; then
        echo -e "${GREEN}✅ PostgreSQL respondendo${NC}"
        break
    fi
    echo "Tentativa $i/30..."
    sleep 2
done
echo ""

# ============================================================================
# 5. EXECUTAR MIGRATIONS SQL
# ============================================================================
echo -e "${BLUE}5. Executando migrations SQL...${NC}"

MIGRATION_1="backend/migrations/001_criar_tabelas_os_completo.sql"
MIGRATION_2="backend/migrations/002_adicionar_campos_essenciais_os.sql"

if [ -f "$MIGRATION_1" ]; then
    echo "Executando: $MIGRATION_1"
    docker-compose exec -T postgres psql -U postgres -d loja_informatica -f /dev/stdin < "$MIGRATION_1"
    echo -e "${GREEN}✅ Migration 001 concluída${NC}"
else
    echo -e "${YELLOW}⚠️  Migration 001 não encontrada${NC}"
fi

if [ -f "$MIGRATION_2" ]; then
    echo "Executando: $MIGRATION_2"
    docker-compose exec -T postgres psql -U postgres -d loja_informatica -f /dev/stdin < "$MIGRATION_2"
    echo -e "${GREEN}✅ Migration 002 concluída${NC}"
else
    echo -e "${YELLOW}⚠️  Migration 002 não encontrada${NC}"
fi
echo ""

# ============================================================================
# 6. VERIFICAR SAÚDE DO SERVIDOR
# ============================================================================
echo -e "${BLUE}6. Verificando saúde do servidor...${NC}"
sleep 5

# Aguardar FastAPI iniciar
echo "Aguardando FastAPI iniciar..."
for i in {1..30}; do
    if curl -s http://localhost:8000/docs &> /dev/null; then
        echo -e "${GREEN}✅ FastAPI respondendo${NC}"
        break
    fi
    echo "Tentativa $i/30..."
    sleep 2
done

# Testar endpoints básicos
echo ""
echo "Testando endpoints..."

# Verificar se servidor está UP
if curl -s http://localhost:8000/docs &> /dev/null; then
    echo -e "${GREEN}✅ API FastAPI disponível em http://localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠️  API FastAPI não respondendo ainda${NC}"
fi

echo ""

# ============================================================================
# 7. RESUMO FINAL
# ============================================================================
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ SERVIDOR INICIALIZADO COM SUCESSO${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "📍 Serviços disponíveis:"
echo "   🔵 FastAPI (Backend):    http://localhost:8000"
echo "   📚 Swagger Docs:         http://localhost:8000/docs"
echo "   🗄️  PostgreSQL:          localhost:5432"
echo "   💾 pgAdmin:              http://localhost:5050"
echo ""
echo "📝 Comandos úteis:"
echo "   Ver logs:                docker-compose logs -f backend"
echo "   Parar servidor:          docker-compose down"
echo "   Reiniciar:               docker-compose restart"
echo ""
echo "🧪 Testar API:"
echo "   curl http://localhost:8000/docs"
echo ""
echo "✅ Sistema pronto para uso!"
echo ""
