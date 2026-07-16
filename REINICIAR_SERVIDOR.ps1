# Script PowerShell para reiniciar servidores
# Execute: .\REINICIAR_SERVIDOR.ps1

# Se der erro de permissão, execute:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

$ProjectDir = "C:\Users\User\loja\Sistema-de-Gest-o-de-Loja-de-Inform-tica"
Set-Location $ProjectDir

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "🔄 Reiniciando servidores..." -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Parar containers
Write-Host "⏹️  Parando containers..." -ForegroundColor Yellow
docker compose down

# Aguardar
Start-Sleep -Seconds 2

# Iniciar containers
Write-Host ""
Write-Host "🚀 Iniciando containers..." -ForegroundColor Green
docker compose up -d

# Aguardar serviços ficarem prontos
Write-Host ""
Write-Host "⏳ Aguardando serviços ficarem prontos (10 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar status
Write-Host ""
Write-Host "📊 Status dos serviços:" -ForegroundColor Cyan
docker compose ps

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "✅ Servidores reiniciados!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "🔧 Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "🗄️  PgAdmin: http://localhost:5050" -ForegroundColor White
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Abrir navegador (opcional)
$response = Read-Host "Deseja abrir o navegador? (S/N)"
if ($response -eq "S" -or $response -eq "s") {
    Start-Process "http://localhost:3000"
}
