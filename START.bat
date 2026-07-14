@echo off
REM 🚀 Script para iniciar a aplicação completa (Windows)
REM Uso: START.bat

setlocal enabledelayedexpansion

echo.
echo ============================================
echo   🚀 Sistema Híbrido FastAPI + Node.js
echo ============================================
echo.

REM Verificar pré-requisitos
echo 📋 Verificando pré-requisitos...

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado
    echo Instale em: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python encontrado:
python --version

REM Verificar Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js não encontrado
    echo Instale em: https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js encontrado:
node --version

REM Verificar Docker (opcional)
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker não encontrado (PostgreSQL local será necessário)
    set DOCKER_AVAILABLE=false
) else (
    echo ✅ Docker encontrado
    set DOCKER_AVAILABLE=true
)

echo.
echo 📦 Instalando dependências...
echo.

REM Instalar dependências do Backend
if not exist "backend\venv" (
    echo 📦 Criando ambiente virtual Python...
    cd backend
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt 2>nul || (
        pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-multipart requests email-validator
    )
    cd ..
    echo ✅ Backend pronto
) else (
    echo ✅ Backend já instalado
)

REM Instalar dependências do Node.js (procurar em vários locais)
if exist "atendimento" (
    if not exist "atendimento\node_modules" (
        echo 📦 Instalando dependências Node.js...
        cd atendimento
        call npm install
        cd ..
        echo ✅ Node.js pronto
    ) else (
        echo ✅ Node.js já instalado
    )
) else if exist "..\atendimento" (
    if not exist "..\atendimento\node_modules" (
        echo 📦 Instalando dependências Node.js...
        cd ..\atendimento
        call npm install
        cd ..\Sistema-de-Gest-o-de-Loja-de-Inform-tica
        echo ✅ Node.js pronto
    ) else (
        echo ✅ Node.js já instalado
    )
) else (
    echo ⚠️  Pasta 'atendimento' não encontrada
    echo Procure pela pasta e inicialize Node.js manualmente
)

echo.
echo 🚀 Iniciando serviços...
echo.

REM Iniciar Docker se disponível
if "%DOCKER_AVAILABLE%"=="true" (
    echo 🐘 Iniciando PostgreSQL com Docker...
    docker-compose up -d postgres pgadmin
    echo ✅ PostgreSQL rodando em localhost:5432
    echo ✅ pgAdmin rodando em http://localhost:5050
    timeout /t 3
)

echo.
echo ⚠️  VOCÊ PRECISA ABRIR 2 NOVOS TERMINALS PARA INICIAR OS SERVIDORES
echo.
echo 📋 Terminal 2 - FastAPI Backend:
echo cd backend
echo venv\Scripts\activate
echo python main.py
echo.
echo 📋 Terminal 3 - Node.js Atendimento:
echo cd atendimento
echo node server/index.js
echo.
echo 🌐 URLs de Acesso:
echo   FastAPI: http://localhost:8000
echo   Docs:    http://localhost:8000/docs
echo   Node.js: http://localhost:3000
echo   pgAdmin: http://localhost:5050
echo.
echo 🎉 Preparação concluída!
echo.
pause
