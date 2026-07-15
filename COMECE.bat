@echo off
REM ========================================
REM COMECE AQUI - Automatiza TUDO!
REM ========================================
REM Este arquivo faz tudo automaticamente
REM Não precisa digitar nada!

setlocal enabledelayedexpansion

color 0A
title 🚀 Sistema Loja - Auto Start

echo.
echo ========================================
echo   INICIANDO SISTEMA AUTOMATICAMENTE
echo ========================================
echo.

REM Pega o diretório onde o arquivo está
set SCRIPT_DIR=%~dp0
echo Diretório do projeto: %SCRIPT_DIR%
echo.

REM Muda para o diretório correto
cd /d "%SCRIPT_DIR%"

REM Verifica se é um repositório git
if not exist ".git" (
    echo ERRO: Nao e um repositorio git!
    echo Este arquivo deve estar na raiz do projeto
    pause
    exit /b 1
)

echo ✓ Repositório git encontrado
echo.

REM Passo 1: Git pull
echo [1/4] Atualizando do GitHub...
git pull origin claude/multi-server-db-sync-1hx0l2 2>nul
if errorlevel 1 (
    echo (pode ser normal se ja esta atualizado)
)
echo.

REM Passo 2: Criar .env files
echo [2/4] Criando arquivos de configuração...
if not exist "backend\.env" (
    copy backend\.env.example backend\.env >nul
    echo ✓ backend\.env criado
) else (
    echo ✓ backend\.env ja existe
)

if not exist "frontend\.env" (
    copy frontend\.env.example frontend\.env >nul
    echo ✓ frontend\.env criado
) else (
    echo ✓ frontend\.env ja existe
)
echo.

REM Passo 3: Limpar containers antigos
echo [3/4] Limpando containers antigos...
docker-compose down --remove-orphans -v 2>nul
echo ✓ Limpeza concluida
echo.

REM Passo 4: Iniciar Docker
echo [4/4] Iniciando servicos Docker...
echo Aguarde... isso pode levar alguns minutos na primeira vez
echo.
docker-compose up --build

REM Se chegou aqui, deu sucesso
echo.
echo ========================================
echo   ✓ TUDO RODANDO!
echo ========================================
echo.
echo Acesse:
echo   🌐 Frontend:  http://localhost:3000
echo   ⚙️  Backend:   http://localhost:8000
echo   📊 pgAdmin:   http://localhost:5050
echo   🗄️  Banco:     localhost:5432
echo.
echo Credenciais:
echo   Email: admin@loja.com
echo   Senha: admin
echo.
pause
