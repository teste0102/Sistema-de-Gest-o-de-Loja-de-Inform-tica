# PowerShell Script para abrir PowerShell no diretório do projeto
# Execute este arquivo: powershell -File abrir-powershell.ps1

# Pega o diretório onde o script está
$projectDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# Muda para o diretório
Set-Location $projectDir

# Limpa a tela
Clear-Host

# Exibe mensagem de boas-vindas
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Sistema de Gestão de Loja" -ForegroundColor Green
Write-Host "  Diretório: $projectDir" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Comandos prontos:" -ForegroundColor Yellow
Write-Host "  1. Iniciar tudo:"
Write-Host "     .\COMECE.bat" -ForegroundColor White
Write-Host ""
Write-Host "  2. Setup manual:"
Write-Host "     .\setup.bat" -ForegroundColor White
Write-Host ""
Write-Host "  3. Ver status:"
Write-Host "     docker-compose ps" -ForegroundColor White
Write-Host ""
Write-Host "  4. Parar tudo:"
Write-Host "     docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "Acesse:" -ForegroundColor Yellow
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "  pgAdmin:   http://localhost:5050" -ForegroundColor Cyan
Write-Host ""
