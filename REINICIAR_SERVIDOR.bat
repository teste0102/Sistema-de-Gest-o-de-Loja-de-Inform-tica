@echo off
REM Script para reiniciar servidores no Windows
REM Coloque este arquivo na área de trabalho e execute-o

cd /d C:\Users\User\loja\Sistema-de-Gest-o-de-Loja-de-Inform-tica

echo.
echo ================================
echo 🔄 Reiniciando servidores...
echo ================================
echo.

REM Parar containers
echo ⏹️  Parando containers...
docker compose down

REM Aguardar
timeout /t 2 /nobreak

REM Iniciar containers
echo.
echo 🚀 Iniciando containers...
docker compose up -d

REM Aguardar serviços ficarem prontos
echo.
echo ⏳ Aguardando serviços ficarem prontos (10 segundos)...
timeout /t 10 /nobreak

REM Verificar status
echo.
echo 📊 Status dos serviços:
docker compose ps

echo.
echo ================================
echo ✅ Servidores reiniciados!
echo ================================
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8000
echo 🗄️  PgAdmin: http://localhost:5050
echo ================================
echo.
echo Pressione qualquer tecla para sair...
pause
