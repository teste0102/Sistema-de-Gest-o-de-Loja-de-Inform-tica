#!/bin/bash
# Setup Script for Sistema de Gestão de Loja de Informática
# This script prepares the environment for running with Docker Compose

set -e

echo "🔧 Setting up Sistema de Gestão de Loja de Informática..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Create backend .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}Creating backend/.env...${NC}"
    cp backend/.env.example backend/.env
    sed -i 's|^# Docker Compose Configuration|Docker Compose Configuration|' backend/.env
    echo -e "${GREEN}✓ Created backend/.env${NC}"
else
    echo -e "${GREEN}✓ backend/.env already exists${NC}"
fi

# Create frontend .env file if it doesn't exist
if [ ! -f "frontend/.env" ]; then
    echo -e "${YELLOW}Creating frontend/.env...${NC}"
    cp frontend/.env.example frontend/.env
    echo -e "${GREEN}✓ Created frontend/.env${NC}"
else
    echo -e "${GREEN}✓ frontend/.env already exists${NC}"
fi

echo ""
echo -e "${GREEN}✓ Environment setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Start the application:"
echo "     docker-compose up --build"
echo ""
echo "  2. Access the services:"
echo "     - Frontend:  http://localhost:3000"
echo "     - Backend:   http://localhost:8000"
echo "     - pgAdmin:   http://localhost:5050"
echo "     - Database:  localhost:5432"
echo ""
echo -e "${YELLOW}pgAdmin credentials:${NC}"
echo "  Email:    admin@loja.com"
echo "  Password: admin"
echo ""
echo -e "${YELLOW}Database credentials:${NC}"
echo "  User:     postgres"
echo "  Password: postgres"
echo "  Database: loja_informatica"
echo ""
