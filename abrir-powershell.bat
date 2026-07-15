@echo off
REM Abre PowerShell no diretório do projeto
REM Quando você double-click, abre uma nova janela de PowerShell já na pasta certa

REM Pega o diretório do arquivo .bat
set PROJECT_DIR=%~dp0

REM Abre PowerShell nova janela no diretório correto
start powershell.exe -NoExit -Command "cd '%PROJECT_DIR%'; Write-Host '========================================' -ForegroundColor Green; Write-Host '  Sistema de Gestão de Loja de Informática' -ForegroundColor Green; Write-Host '  Diretório: %PROJECT_DIR%' -ForegroundColor Cyan; Write-Host '========================================' -ForegroundColor Green; Write-Host ''; Write-Host 'Próximos comandos:' -ForegroundColor Yellow; Write-Host '  .\COMECE.bat                    # Inicia TUDO automaticamente' -ForegroundColor White; Write-Host '  docker-compose ps              # Ver status dos containers' -ForegroundColor White; Write-Host '  docker-compose down            # Parar tudo' -ForegroundColor White; Write-Host '';"
