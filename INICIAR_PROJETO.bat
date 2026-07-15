@echo off
REM ============================================================================
REM SCRIPT DE INICIALIZAÇÃO - LOJA DE INFORMÁTICA
REM Caminho fixo para todas as operações
REM ============================================================================

cd /d "C:\Windows\system32\Sistema-de-Gest-o-de-Loja-de-Inform-tica"

REM Executar script PowerShell
powershell -ExecutionPolicy Bypass -File "%CD%\INICIAR_PROJETO.ps1"

pause
