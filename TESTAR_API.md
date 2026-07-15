# 🧪 GUIA DE TESTES - API LOJA DE INFORMÁTICA

## 📋 Pré-requisitos
- ✅ Docker Compose rodando (`docker compose up -d`)
- ✅ Migrations executadas
- ✅ Servidor respondendo em `http://localhost:8000`

---

## 🚀 Iniciar Testes

### 1. Abrir Swagger (Documentação Interativa)
```powershell
Start-Process "http://localhost:8000/docs"
```

---

## 📝 Sequência de Testes Recomendada

### FASE 1: CLIENTES
```
GET  /api/clientes/              ← Listar clientes
POST /api/clientes/              ← Criar novo cliente
GET  /api/clientes/{cliente_id}  ← Obter cliente específico
```

**Exemplo POST (criar cliente):**
```json
{
  "nome": "Samsung Service",
  "email": "samsung@example.com",
  "telefone": "(11) 98765-4321",
  "cpf_cnpj": "12345678901234",
  "endereco": "Av Paulista, 1000",
  "cidade": "São Paulo",
  "estado": "SP",
  "cep": "01310-100"
}
```

---

### FASE 2: NÚMEROS OS (Ordem de Serviço)
```
POST /api/os/gerar-numero              ← Gerar novo número OS
GET  /api/os/cliente/{cliente_id}      ← Listar OS do cliente
GET  /api/os/numero/{numero_os}        ← Buscar OS por número
GET  /api/os/{ordem_id}                ← Obter detalhes da OS
POST /api/os/validar-numero            ← Validar formato OS
```

**Teste 1: Gerar Número OS**
```
POST /api/os/gerar-numero
Parâmetro: cliente_id = 1

Resposta esperada:
{
  "ok": true,
  "numero_os": "OS-20260715-00001",
  "ordem_id": 1,
  "status": "aberta"
}
```

---

### FASE 3: SENHAS (PIN/Padrão/Nenhuma)
```
POST   /api/os/{ordem_id}/senhas              ← Criar senha
GET    /api/os/{ordem_id}/senhas              ← Obter info senha
DELETE /api/os/{ordem_id}/senhas              ← Deletar senha
POST   /api/os/{ordem_id}/senhas/gerar        ← Gerar senha aleatória
POST   /api/os/{ordem_id}/senhas/avaliar      ← Avaliar força
```

**Teste 1: Criar PIN**
```
POST /api/os/1/senhas

Body (JSON):
{
  "tipo": "pin",
  "valor": "1234",
  "tamanho_pin": 4
}

Resposta esperada:
{
  "ok": true,
  "senha_id": "pwd_xxx",
  "tipo": "pin",
  "ordem_id": 1
}
```

**Teste 2: Criar Padrão**
```
POST /api/os/1/senhas

Body:
{
  "tipo": "padrao",
  "coordenadas": [[0,0], [1,1], [2,2], [1,0]]
}
```

**Teste 3: Criar Nenhuma (desbloqueado)**
```
POST /api/os/1/senhas

Body:
{
  "tipo": "nenhuma"
}
```

---

### FASE 4: FOTOS
```
POST /api/os/{ordem_id}/fotos/upload   ← Upload de foto
GET  /api/os/{ordem_id}/fotos          ← Listar fotos
GET  /api/os/{ordem_id}/fotos/{foto_id} ← Obter foto específica
DELETE /api/os/{ordem_id}/fotos/{foto_id} ← Deletar foto
GET  /api/os/recursos/tipos-dano       ← Listar tipos de dano
```

**Teste 1: Upload de Foto**
```
POST /api/os/1/fotos/upload

Form data:
- arquivo: (selecionar imagem JPG/PNG)
- descricao: "Dano na tela frontal"
- tipo_dano: "tela"

Tipos de dano disponíveis:
- tela
- botao
- bateria
- agua
- queda
- conector
- camera
- placa
- vazio
- outros
```

---

### FASE 5: LAUDO TÉCNICO
```
POST /api/os/{ordem_id}/laudo              ← Criar laudo
GET  /api/os/{ordem_id}/laudo              ← Obter laudo
POST /api/os/{ordem_id}/laudo/validar      ← Validar integridade
POST /api/os/{ordem_id}/laudo/assinar      ← Assinar (caneta USB)
GET  /api/os/{ordem_id}/laudo/resumo       ← Gerar resumo
DELETE /api/os/{ordem_id}/laudo            ← Deletar laudo
```

**Teste 1: Criar Laudo**
```
POST /api/os/1/laudo

Body:
{
  "danos": [
    {
      "tipo": "tela",
      "descricao": "Trinca na parte superior",
      "severidade": "grave",
      "foto_ids": ["foto_1", "foto_2"],
      "observacoes": "Impacto frontal"
    }
  ],
  "observacoes_gerais": "Dispositivo chegou com dano frontal",
  "recomendacoes": ["Trocar tela", "Limpar internamente"],
  "valor_conserto": 450.00
}

Severidades válidas: leve, media, grave
```

---

### FASE 6: SINCRONIZAÇÃO
```
POST   /api/sync/enfileirar              ← Enfileirar operação
GET    /api/sync/fila                    ← Ver fila de sync
GET    /api/sync/status                  ← Status geral de sync
POST   /api/sync/servidores              ← Registrar servidor remoto
POST   /api/sync/detectar-conflito       ← Detectar conflito
POST   /api/sync/resolver-conflito       ← Resolver conflito
GET    /api/sync/estrategias             ← Listar estratégias
POST   /api/sync/hash                    ← Gerar hash de dados
```

**Teste 1: Enfileirar Operação**
```
POST /api/sync/enfileirar

Body:
{
  "tabela": "ordens_servico",
  "operacao": "update",
  "registro_id": 1,
  "dados": {
    "status": "em_analise",
    "observacoes": "Testando sincronização"
  }
}
```

---

## ✅ Checklist de Testes

- [ ] Cliente criado com sucesso
- [ ] Número OS gerado (formato OS-YYYYMMDD-XXXXX)
- [ ] Senha PIN criada e criptografada
- [ ] Senha Padrão criada com coordenadas
- [ ] Foto enviada e armazenada
- [ ] Laudo técnico criado com assinatura RSA-2048
- [ ] Validação de integridade do laudo passou
- [ ] Operação enfileirada para sincronização
- [ ] Status de sync mostrando fila

---

## 🐛 Troubleshooting

### API não responde
```powershell
docker compose ps
docker compose logs backend --tail 50
```

### Erro de conexão com banco de dados
```powershell
docker compose exec -T postgres psql -U postgres -c "SELECT 1"
```

### Migrations não executadas
```powershell
.\EXECUTAR_MIGRATIONS.ps1
```

### Limpar e recomeçar
```powershell
docker compose down -v
docker compose build --no-cache
docker compose up -d
.\EXECUTAR_MIGRATIONS.ps1
```

---

## 📊 Próximos Passos

1. ✅ Confirmar que todos os testes passam
2. ⬜ Desenvolver Frontend (React)
3. ⬜ Criar fluxo completo de OS (cliente → senha → fotos → laudo → assinatura)
4. ⬜ Implementar sincronização multi-servidor
5. ⬜ Deploy em produção

---

**Dúvidas?** Verifique a documentação em `http://localhost:8000/docs` 🚀
