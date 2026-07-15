# ============================================================================
# SCRIPT DE INICIALIZAÇÃO DO PROJETO - LOJA DE INFORMÁTICA
# Caminho fixo e automático para todas as operações
# ============================================================================

# Definir variáveis globais
$PROJETO_PATH = "C:\Windows\system32\Sistema-de-Gest-o-de-Loja-de-Inform-tica"
$API_URL = "http://localhost:8000"
$FRONTEND_URL = "http://localhost:3000"
$PGADMIN_URL = "http://localhost:5050"

# Mudar para diretório do projeto
Set-Location $PROJETO_PATH
Write-Host "✅ Navegado para: $PROJETO_PATH" -ForegroundColor Green

# Menu de opções
Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   LOJA DE INFORMÁTICA - PAINEL DE CONTROLE                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "SERVIDOR:" -ForegroundColor Yellow
Write-Host "  [1] Ver status dos containers"
Write-Host "  [2] Subir servidor (docker compose up -d)"
Write-Host "  [3] Parar servidor (docker compose down)"
Write-Host "  [4] Reconstruir servidor (docker compose build --no-cache)"
Write-Host "  [5] Ver logs do backend"
Write-Host ""

Write-Host "BANCO DE DADOS:" -ForegroundColor Yellow
Write-Host "  [6] Executar migrations (001 e 002)"
Write-Host "  [7] Abrir pgAdmin em navegador"
Write-Host "  [8] Ver status do PostgreSQL"
Write-Host ""

Write-Host "API & FRONTEND:" -ForegroundColor Yellow
Write-Host "  [9] Abrir Swagger API (documentação)"
Write-Host "  [10] Abrir Frontend (React)"
Write-Host "  [11] Testar conexão com API"
Write-Host ""

Write-Host "UTILITÁRIOS:" -ForegroundColor Yellow
Write-Host "  [12] Abrir explorador de arquivos no projeto"
Write-Host "  [13] Ver estrutura do projeto"
Write-Host "  [14] Verificar Git status"
Write-Host "  [15] Sair"
Write-Host ""

# Capturar entrada
$opcao = Read-Host "Escolha uma opção (1-15)"

switch($opcao) {
    "1" {
        Write-Host "`n📊 Status dos containers:" -ForegroundColor Cyan
        docker ps
    }

    "2" {
        Write-Host "`n🚀 Iniciando servidor..." -ForegroundColor Cyan
        docker compose up -d
        Start-Sleep -Seconds 3
        Write-Host "`n✅ Servidor iniciado!" -ForegroundColor Green
        Write-Host "   API: $API_URL/docs" -ForegroundColor Green
        Write-Host "   Frontend: $FRONTEND_URL" -ForegroundColor Green
        Write-Host "   pgAdmin: $PGADMIN_URL" -ForegroundColor Green
    }

    "3" {
        Write-Host "`n🛑 Parando servidor..." -ForegroundColor Cyan
        docker compose down
        Write-Host "✅ Servidor parado!" -ForegroundColor Green
    }

    "4" {
        Write-Host "`n🔄 Reconstruindo servidor (pode levar alguns minutos)..." -ForegroundColor Cyan
        docker compose build --no-cache
        Write-Host "✅ Servidor reconstruído!" -ForegroundColor Green
        Write-Host "`nPróximo passo: Execute a opção [2] para subir" -ForegroundColor Yellow
    }

    "5" {
        Write-Host "`n📋 Logs do Backend (últimas 30 linhas):" -ForegroundColor Cyan
        docker compose logs backend --tail 30
    }

    "6" {
        Write-Host "`n💾 Executando migrations..." -ForegroundColor Cyan
        Write-Host "   [1/2] Executando 001_initial_schema.sql..." -ForegroundColor Yellow
        docker compose exec -T postgres psql -U postgres -d loja_informatica -f /migrations/001_initial_schema.sql
        Write-Host "   [2/2] Executando 002_sync_tables.sql..." -ForegroundColor Yellow
        docker compose exec -T postgres psql -U postgres -d loja_informatica -f /migrations/002_sync_tables.sql
        Write-Host "`n✅ Migrations executadas com sucesso!" -ForegroundColor Green
    }

    "7" {
        Write-Host "`n🌐 Abrindo pgAdmin..." -ForegroundColor Cyan
        Start-Process "$PGADMIN_URL"
        Write-Host "✅ pgAdmin aberto no navegador!" -ForegroundColor Green
        Write-Host "   URL: $PGADMIN_URL" -ForegroundColor Green
        Write-Host "   Credenciais:" -ForegroundColor Yellow
        Write-Host "   - Email: admin@admin.com" -ForegroundColor Yellow
        Write-Host "   - Senha: admin" -ForegroundColor Yellow
    }

    "8" {
        Write-Host "`n🗄️ Status do PostgreSQL:" -ForegroundColor Cyan
        docker compose exec -T postgres psql -U postgres -c "SELECT version();"
        Write-Host "`n📊 Bancos de dados:" -ForegroundColor Cyan
        docker compose exec -T postgres psql -U postgres -l
    }

    "9" {
        Write-Host "`n📚 Abrindo documentação da API (Swagger)..." -ForegroundColor Cyan
        Start-Process "$API_URL/docs"
        Write-Host "✅ Swagger aberto!" -ForegroundColor Green
        Write-Host "   URL: $API_URL/docs" -ForegroundColor Green
    }

    "10" {
        Write-Host "`n🎨 Abrindo Frontend..." -ForegroundColor Cyan
        Start-Process "$FRONTEND_URL"
        Write-Host "✅ Frontend aberto!" -ForegroundColor Green
        Write-Host "   URL: $FRONTEND_URL" -ForegroundColor Green
    }

    "11" {
        Write-Host "`n🔗 Testando conexão com API..." -ForegroundColor Cyan
        try {
            $response = Invoke-WebRequest -Uri "$API_URL/docs" -UseBasicParsing
            Write-Host "✅ API respondendo normalmente!" -ForegroundColor Green
            Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Green
        } catch {
            Write-Host "❌ API não está respondendo" -ForegroundColor Red
            Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "   Verifique se o servidor está rodando: docker compose up -d" -ForegroundColor Yellow
        }
    }

    "12" {
        Write-Host "`n📁 Abrindo explorador de arquivos..." -ForegroundColor Cyan
        Invoke-Item $PROJETO_PATH
    }

    "13" {
        Write-Host "`n📂 Estrutura do Projeto:" -ForegroundColor Cyan
        Write-Host @"
$PROJETO_PATH
├── backend/
│   ├── main.py (FastAPI app)
│   ├── database.py (SQLAlchemy)
│   ├── models.py (Modelos do BD)
│   ├── requirements.txt
│   ├── routes/ (Endpoints)
│   │   ├── clientes.py
│   │   ├── ordens.py
│   │   ├── numeros_os.py ✅ (OS Numbers)
│   │   ├── senhas.py ✅ (Passwords)
│   │   ├── fotos.py ✅ (Photos)
│   │   ├── laudo.py ✅ (Reports)
│   │   ├── sync.py ✅ (Sync)
│   │   └── financeiro.py
│   ├── services/ (Lógica de negócio)
│   │   ├── numero_os_service.py ✅
│   │   ├── senha_service.py ✅
│   │   ├── foto_service.py ✅
│   │   ├── laudo_service.py ✅
│   │   ├── replay_service.py ✅
│   │   └── sync_service.py ✅
│   ├── utils/
│   │   └── crypto_service.py (AES-256, RSA-2048)
│   └── migrations/
│       ├── 001_initial_schema.sql
│       └── 002_sync_tables.sql
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .github/
├── .gitignore
└── README.md
"@
    }

    "14" {
        Write-Host "`n📌 Status do Git:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Commit atual:" -ForegroundColor Yellow
        git log --oneline -1
        Write-Host ""
        Write-Host "Branch:" -ForegroundColor Yellow
        git branch --show-current
        Write-Host ""
        Write-Host "Status:" -ForegroundColor Yellow
        git status
    }

    "15" {
        Write-Host "`n👋 Até logo!" -ForegroundColor Green
        exit
    }

    default {
        Write-Host "`n❌ Opção inválida!" -ForegroundColor Red
    }
}

Write-Host "`n" -ForegroundColor Cyan
$continuar = Read-Host "Deseja executar outra ação? (S/N)"
if ($continuar -eq "S" -or $continuar -eq "s") {
    & $PROFILE
}
