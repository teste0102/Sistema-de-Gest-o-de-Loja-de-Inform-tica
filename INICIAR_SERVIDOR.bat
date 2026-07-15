@echo off
REM ============================================================================
REM Script de Inicialização - Sistema de OS (Windows)
REM Executa migrations, valida ambiente e inicia servidor
REM ============================================================================

setlocal enabledelayedexpansion

color 0A
cls
echo ================================
echo 🚀 INICIALIZANDO SERVIDOR OS
echo ================================
echo.

REM ============================================================================
REM 1. VERIFICAR DOCKER
REM ============================================================================
echo [1/6] Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ❌ Docker nao encontrado. Instale Docker Desktop primeiro.
    pause
    exit /b 1
)
color 0A
echo ✅ Docker disponivel
echo.

REM ============================================================================
REM 2. VERIFICAR ARQUIVO .env
REM ============================================================================
echo [2/6] Verificando configuracoes (.env)...
if not exist ".env" (
    color 0E
    echo ⚠️  Arquivo .env nao encontrado
    echo Criando arquivo .env padrao...
    (
        echo # Database
        echo DATABASE_URL=postgresql://postgres:postgres@postgres:5432/loja_informatica
        echo POSTGRES_USER=postgres
        echo POSTGRES_PASSWORD=postgres
        echo POSTGRES_DB=loja_informatica
        echo.
        echo # FastAPI
        echo API_HOST=0.0.0.0
        echo API_PORT=8000
        echo SECRET_KEY=sua-chave-secreta-super-segura-aqui-32-caracteres
        echo.
        echo # Node.js
        echo NODE_ENV=production
        echo PORT=3000
        echo.
        echo # Paths
        echo DATA_PATH=/data
        echo FOTOS_PATH=/data/fotos
    ) > .env
    color 0A
    echo ✅ Arquivo .env criado
) else (
    color 0A
    echo ✅ Arquivo .env encontrado
)
echo.

REM ============================================================================
REM 3. CRIAR DIRETÓRIOS DE DADOS
REM ============================================================================
echo [3/6] Criando diretorios de dados...
if not exist "data\fotos" mkdir data\fotos
if not exist "data\postgres" mkdir data\postgres
color 0A
echo ✅ Diretorios criados
echo.

REM ============================================================================
REM 4. INICIAR DOCKER COMPOSE
REM ============================================================================
echo [4/6] Iniciando servicos Docker...
docker-compose up -d

echo Aguardando servicos iniciarem...
timeout /t 10 /nobreak

color 0A
echo ✅ Docker Compose iniciado
echo.

REM ============================================================================
REM 5. EXECUTAR MIGRATIONS SQL
REM ============================================================================
echo [5/6] Executando migrations SQL...

if exist "backend\migrations\001_criar_tabelas_os_completo.sql" (
    echo Executando: 001_criar_tabelas_os_completo.sql
    docker-compose exec -T postgres psql -U postgres -d loja_informatica -f /dev/stdin ^< backend\migrations\001_criar_tabelas_os_completo.sql
    color 0A
    echo ✅ Migration 001 concluida
) else (
    color 0E
    echo ⚠️  Migration 001 nao encontrada
)

if exist "backend\migrations\002_adicionar_campos_essenciais_os.sql" (
    echo Executando: 002_adicionar_campos_essenciais_os.sql
    docker-compose exec -T postgres psql -U postgres -d loja_informatica -f /dev/stdin ^< backend\migrations\002_adicionar_campos_essenciais_os.sql
    color 0A
    echo ✅ Migration 002 concluida
) else (
    color 0E
    echo ⚠️  Migration 002 nao encontrada
)
echo.

REM ============================================================================
REM 6. RESUMO FINAL
REM ============================================================================
color 0A
echo ================================
echo ✅ SERVIDOR INICIALIZADO COM SUCESSO
echo ================================
echo.
echo 📍 Servicos disponiveis:
echo    🔵 FastAPI (Backend):    http://localhost:8000
echo    📚 Swagger Docs:         http://localhost:8000/docs
echo    🗄️  PostgreSQL:          localhost:5432
echo    💾 pgAdmin:              http://localhost:5050
echo.
echo 📝 Comandos uteis:
echo    Ver logs:                docker-compose logs -f backend
echo    Parar servidor:          docker-compose down
echo    Reiniciar:               docker-compose restart
echo.
echo 🧪 Testar API:
echo    Abra no navegador: http://localhost:8000/docs
echo.
echo ✅ Sistema pronto para uso!
echo.
pause
