#!/bin/bash

# Script para reiniciar todos os serviços Docker
# Execute: chmod +x REINICIAR_SERVIDOR.sh
# Depois: ./REINICIAR_SERVIDOR.sh

PROJECT_DIR="/home/user/Sistema-de-Gest-o-de-Loja-de-Inform-tica"
cd "$PROJECT_DIR"

echo "🔄 Reiniciando servidores..."
echo "================================"

# Parar containers
echo "⏹️  Parando containers..."
docker compose down

# Aguardar um pouco
sleep 2

# Iniciar containers
echo "🚀 Iniciando containers..."
docker compose up -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

# Verificar status
echo ""
echo "📊 Status dos serviços:"
docker compose ps

echo ""
echo "✅ Servidores reiniciados!"
echo "================================"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "🗄️  PgAdmin: http://localhost:5050"
echo "================================"
