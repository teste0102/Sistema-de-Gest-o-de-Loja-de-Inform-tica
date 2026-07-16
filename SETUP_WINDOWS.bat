@echo off
REM Script Setup para Windows - Wrapper para PowerShell

title Setup - Sistema de Gestao de Loja

cd /d C:\Users\User\loja\Sistema-de-Gest-o-de-Loja-de-Inform-tica

echo.
echo ====================================================
echo   SETUP - Sistema de Gestao de Loja
echo ====================================================
echo.

REM Executar PowerShell script
powershell -ExecutionPolicy RemoteSigned -File "SETUP_WINDOWS.ps1"

pause
