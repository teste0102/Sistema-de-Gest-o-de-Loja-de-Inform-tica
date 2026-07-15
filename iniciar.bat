@echo off
REM Script completo de inicialização
REM Faz: git pull + setup + docker-compose up
REM Execute este arquivo fazendo double-click

color 0A
title Sistema de Gestão de Loja de Informática - Inicialização

echo.
echo ========================================
echo   Sistema de Gestao de Loja
echo   Inicializacao Automatica
echo ========================================
echo.

REM Pega o caminho do arquivo .bat
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo [1/5] Verificando Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Git nao esta instalado!
    pause
    exit /b 1
)
echo OK: Git encontrado

echo.
echo [2/5] Atualizando arquivos do GitHub...
git pull origin claude/multi-server-db-sync-1hx0l2
if errorlevel 1 (
    echo AVISO: git pull falhou (pode ser normal se nao ha mudancas)
)

echo.
echo [3/5] Executando setup...
if exist "setup.bat" (
    call setup.bat
) else (
    echo ERRO: setup.bat nao encontrado!
    pause
    exit /b 1
)

echo.
echo [4/5] Limpando containers antigos...
docker-compose down --remove-orphans -v
if errorlevel 1 (
    echo AVISO: Pode haver containers antigos - tudo bem
)

echo.
echo [5/5] Iniciando servicos Docker...
echo.
echo Isso pode levar alguns minutos na primeira execucao...
echo Aguarde as mensagens de "Running" para cada servico
echo.
pause
docker-compose up --build

echo.
echo ========================================
echo   Servicos estao rodando!
echo ========================================
echo.
echo Acesse:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   pgAdmin:   http://localhost:5050
echo   Database:  localhost:5432
echo.
echo Credenciais:
echo   Email pgAdmin: admin@loja.com
echo   Senha pgAdmin: admin
echo.
pause
