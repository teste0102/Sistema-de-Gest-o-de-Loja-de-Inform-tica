@echo off
REM ===== INSTALLER PARA WINDOWS =====
REM Sistema de Gestão de Loja de Informática

setlocal enabledelayedexpansion

color 0A
cls

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║     Sistema de Gestão de Loja de Informática - Installer     ║
echo ║                    Windows Version                            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Verificar Python
echo [1/5] Verificando Python 3.11+...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python não encontrado! Instale em https://www.python.org/
    pause
    exit /b 1
)
echo ✓ Python detectado
python --version

REM Verificar Node.js
echo.
echo [2/5] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Node.js não encontrado! Instale em https://nodejs.org/
    pause
    exit /b 1
)
echo ✓ Node.js detectado
node --version
npm --version

REM Instalar Backend
echo.
echo [3/5] Instalando Backend (FastAPI)...
cd backend

if not exist venv (
    echo   Criando ambiente virtual...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo   Instalando dependências...
pip install -r requirements.txt -q

if errorlevel 1 (
    echo ✗ Erro ao instalar dependências do backend
    pause
    exit /b 1
)

REM Criar .env se não existir
if not exist .env (
    copy .env.example .env >nul
    echo   ⚠ Arquivo .env criado. Revise as configurações se necessário.
)

echo ✓ Backend instalado com sucesso

cd ..

REM Instalar Frontend
echo.
echo [4/5] Instalando Frontend (React)...
cd frontend

if not exist node_modules (
    echo   Instalando pacotes npm (pode levar alguns minutos)...
    call npm install -q
)

if errorlevel 1 (
    echo ✗ Erro ao instalar dependências do frontend
    pause
    exit /b 1
)

REM Criar .env.local se não existir
if not exist .env.local (
    copy .env.example .env.local >nul
    echo   ⚠ Arquivo .env.local criado
)

echo ✓ Frontend instalado com sucesso

cd ..

REM Resumo Final
echo.
echo [5/5] Resumo da Instalação
echo ════════════════════════════════════════════════════════════════
echo.
echo ✓ Backend: FastAPI + SQLAlchemy pronto
echo ✓ Frontend: React + Bootstrap pronto
echo ✓ Ambiente virtual criado
echo ✓ Pacotes npm instalados
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo 🚀 PRÓXIMOS PASSOS:
echo.
echo 1. Abra 3 terminais (Command Prompt)
echo.
echo    Terminal 1 - Banco de Dados:
echo    docker-compose up postgres pgadmin
echo.
echo    Terminal 2 - Backend:
echo    cd backend
echo    venv\Scripts\activate
echo    python main.py
echo.
echo    Terminal 3 - Frontend:
echo    cd frontend
echo    npm start
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo 🌐 Acessos:
echo   • Backend API:  http://localhost:8000
echo   • Swagger:      http://localhost:8000/docs
echo   • Frontend:     http://localhost:3000
echo   • pgAdmin:      http://localhost:5050
echo.
echo 📚 Veja INSTALACAO.md para mais detalhes
echo.
pause
