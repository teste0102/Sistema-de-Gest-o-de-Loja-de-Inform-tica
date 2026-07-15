@echo off
REM Setup Script for Sistema de Gestão de Loja de Informática
REM This script prepares the environment for running with Docker Compose

setlocal enabledelayedexpansion

echo.
echo 🔧 Setting up Sistema de Gestão de Loja de Informática...
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not installed or not in PATH.
    echo Please install Docker Desktop and ensure it's in your PATH.
    pause
    exit /b 1
)

echo ✓ Docker is installed
echo.

REM Create backend .env file if it doesn't exist
if not exist "backend\.env" (
    echo Creating backend\.env...
    copy backend\.env.example backend\.env >nul
    echo ✓ Created backend\.env
) else (
    echo ✓ backend\.env already exists
)

REM Create frontend .env file if it doesn't exist
if not exist "frontend\.env" (
    echo Creating frontend\.env...
    copy frontend\.env.example frontend\.env >nul
    echo ✓ Created frontend\.env
) else (
    echo ✓ frontend\.env already exists
)

echo.
echo ✓ Environment setup complete!
echo.
echo Next steps:
echo   1. Start the application:
echo      docker-compose up --build
echo.
echo   2. Access the services:
echo      - Frontend:  http://localhost:3000
echo      - Backend:   http://localhost:8000
echo      - pgAdmin:   http://localhost:5050
echo      - Database:  localhost:5432
echo.
echo pgAdmin credentials:
echo   Email:    admin@loja.com
echo   Password: admin
echo.
echo Database credentials:
echo   User:     postgres
echo   Password: postgres
echo   Database: loja_informatica
echo.
pause
