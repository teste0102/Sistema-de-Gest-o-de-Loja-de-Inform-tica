# ============================================================================
# EXECUTAR MIGRATIONS - LOJA DE INFORMATICA
# Script para executar as migrations no banco de dados
# ============================================================================

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   EXECUTANDO MIGRATIONS - BANCO DE DADOS                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$PROJETO_PATH = "C:\Windows\system32\Sistema-de-Gest-o-de-Loja-de-Inform-tica"

# Verificar se está no diretório correto
Set-Location $PROJETO_PATH
Write-Host "📁 Diretorio: $PROJETO_PATH`n" -ForegroundColor Yellow

# Função para executar migration
function Executar-Migration {
    param(
        [string]$numero,
        [string]$arquivo
    )

    Write-Host "[$numero] Executando $arquivo..." -ForegroundColor Cyan

    try {
        docker compose exec -T postgres psql -U postgres -d loja_informatica -f /migrations/$arquivo
        Write-Host "✅ Migration $numero concluída com sucesso!`n" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Erro na migration $numero: $($_.Exception.Message)`n" -ForegroundColor Red
        return $false
    }
}

# Executar migrations
Write-Host "Conectando ao banco de dados..." -ForegroundColor Yellow
Write-Host "Database: loja_informatica" -ForegroundColor Yellow
Write-Host "Usuario: postgres`n" -ForegroundColor Yellow

$resultado1 = Executar-Migration "001" "001_initial_schema.sql"
Start-Sleep -Seconds 2
$resultado2 = Executar-Migration "002" "002_sync_tables.sql"

# Resumo
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   RESUMO DE EXECUÇÃO                                       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($resultado1) {
    Write-Host "✅ Migration 001 (Initial Schema)" -ForegroundColor Green
} else {
    Write-Host "❌ Migration 001 (Initial Schema)" -ForegroundColor Red
}

if ($resultado2) {
    Write-Host "✅ Migration 002 (Sync Tables)" -ForegroundColor Green
} else {
    Write-Host "❌ Migration 002 (Sync Tables)" -ForegroundColor Red
}

Write-Host ""

if ($resultado1 -and $resultado2) {
    Write-Host "🎉 TODAS AS MIGRATIONS EXECUTADAS COM SUCESSO!" -ForegroundColor Green
    Write-Host "`n📊 Proximos passos:" -ForegroundColor Cyan
    Write-Host "  1. Abrir API: Start-Process 'http://localhost:8000/docs'" -ForegroundColor Yellow
    Write-Host "  2. Testar endpoints da OS" -ForegroundColor Yellow
    Write-Host "  3. Criar primeiro cliente e ordem de serviço" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  ALGUMAS MIGRATIONS FALHARAM" -ForegroundColor Yellow
    Write-Host "Verifique os erros acima e tente novamente" -ForegroundColor Yellow
}

Write-Host ""
