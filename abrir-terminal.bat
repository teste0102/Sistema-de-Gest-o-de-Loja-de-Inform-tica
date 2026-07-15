@echo off
REM Abre PowerShell/CMD já no diretório do projeto
REM Execute este arquivo fazendo double-click na pasta do projeto

REM Pega o caminho do arquivo .bat
set PROJECT_DIR=%~dp0

REM Abre PowerShell no diretório correto
start powershell.exe -NoExit -Command "cd '%PROJECT_DIR%'; Write-Host 'Bem-vindo ao Sistema de Gestão de Loja de Informática!' -ForegroundColor Green; Write-Host 'Diretório: %PROJECT_DIR%' -ForegroundColor Cyan; Write-Host ''; Write-Host 'Próximos passos:' -ForegroundColor Yellow; Write-Host '  1. .\setup.bat' -ForegroundColor White; Write-Host '  2. docker-compose up --build' -ForegroundColor White; Write-Host ''"
