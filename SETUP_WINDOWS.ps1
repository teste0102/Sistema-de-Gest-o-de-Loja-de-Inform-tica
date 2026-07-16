# Script Setup para Windows - Prepara tudo automaticamente
# Execute: .\SETUP_WINDOWS.ps1

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        SETUP - Sistema de Gestão de Loja                 ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$ProjectDir = "C:\Users\User\loja\Sistema-de-Gest-o-de-Loja-de-Inform-tica"

# Verificar se está na pasta correta
if (-not (Test-Path $ProjectDir)) {
    Write-Host "❌ Pasta não encontrada: $ProjectDir" -ForegroundColor Red
    Write-Host "Verifique o caminho e tente novamente" -ForegroundColor Yellow
    exit 1
}

Set-Location $ProjectDir
Write-Host "📂 Pasta do projeto: $ProjectDir" -ForegroundColor Green
Write-Host ""

# 1. Git Pull
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "1️⃣  Atualizando código do repositório..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

git fetch origin
git pull origin claude/multi-server-db-sync-1hx0l2

Write-Host "✅ Código atualizado!" -ForegroundColor Green
Write-Host ""

# 2. Verificar scripts
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "2️⃣  Verificando scripts de reinicialização..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$scripts = @(
    "REINICIAR_SERVIDOR.ps1",
    "REINICIAR_SERVIDOR.bat",
    "README_REINICIAR.md"
)

foreach ($script in $scripts) {
    if (Test-Path $script) {
        Write-Host "  ✅ $script" -ForegroundColor Green
    }
    else {
        Write-Host "  ❌ $script (NÃO ENCONTRADO)" -ForegroundColor Red
    }
}
Write-Host ""

# 3. Copiar para Desktop (opcional)
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "3️⃣  Copiar scripts para Desktop?" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$response = Read-Host "Deseja copiar os scripts para Desktop? (S/N)"
if ($response -eq "S" -or $response -eq "s") {
    $DesktopPath = "$env:USERPROFILE\Desktop"
    Copy-Item "REINICIAR_SERVIDOR.ps1" $DesktopPath -Force
    Copy-Item "REINICIAR_SERVIDOR.bat" $DesktopPath -Force
    Copy-Item "README_REINICIAR.md" $DesktopPath -Force
    Copy-Item "QUAL_USAR.txt" $DesktopPath -Force
    Write-Host "✅ Scripts copiados para Desktop!" -ForegroundColor Green
}
else {
    Write-Host "ℹ️  Scripts deixados na pasta do projeto" -ForegroundColor Cyan
}
Write-Host ""

# 4. Mostrar status
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 Status do Git" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
git status
Write-Host ""

# 5. Próximos passos
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "✨ PRÓXIMOS PASSOS:" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "1️⃣  Para reiniciar os servidores agora:" -ForegroundColor White
Write-Host "   .\REINICIAR_SERVIDOR.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "2️⃣  Ou duplo clique em:" -ForegroundColor White
Write-Host "   REINICIAR_SERVIDOR.bat" -ForegroundColor Yellow
Write-Host ""
Write-Host "3️⃣  Acessar depois de reiniciar:" -ForegroundColor White
Write-Host "   • Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "   • Backend:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "   • PgAdmin:   http://localhost:5050" -ForegroundColor Cyan
Write-Host ""
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ Setup concluído!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

$response = Read-Host "Deseja reiniciar os servidores agora? (S/N)"
if ($response -eq "S" -or $response -eq "s") {
    Write-Host ""
    Write-Host "🔄 Reiniciando servidores..." -ForegroundColor Yellow
    .\REINICIAR_SERVIDOR.ps1
}
else {
    Write-Host "ℹ️  Execute REINICIAR_SERVIDOR.ps1 quando estiver pronto" -ForegroundColor Cyan
}
