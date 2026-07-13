"""
routes/sync.py - Sincronização Offline-First
Processa filas de sincronização do cliente
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import SyncQueue, Cliente, OrdemServico, Lancamento
from schemas import SyncRequest, SyncResponse

router = APIRouter()

@router.post("/push", response_model=SyncResponse)
async def sincronizar_push(sync_request: SyncRequest, db: Session = Depends(get_db)):
    """
    Recebe operações offline do cliente e sincroniza com BD
    
    Fluxo:
    1. Cliente envia fila de operações (insert/update/delete)
    2. API processa cada uma
    3. Retorna resultado (sucesso, conflito, erro)
    """
    sincronizados = 0
    conflitos = 0
    erros = []
    
    for item in sync_request.itens:
        try:
            if item.operacao == "insert":
                _processar_insert(db, item)
                sincronizados += 1
                
            elif item.operacao == "update":
                _processar_update(db, item)
                sincronizados += 1
                
            elif item.operacao == "delete":
                _processar_delete(db, item)
                sincronizados += 1
            
            # Marcar como sincronizado
            sync_queue = SyncQueue(
                tabela=item.tabela,
                operacao=item.operacao,
                registro_id=item.registro_id,
                dados=item.dados,
                sincronizado=True
            )
            db.add(sync_queue)
            
        except Exception as e:
            erros.append(f"{item.tabela}:{item.operacao}:{str(e)}")
    
    db.commit()
    
    return SyncResponse(
        status="success" if not erros else "error",
        sincronizados=sincronizados,
        conflitos=conflitos,
        erros=erros
    )

def _processar_insert(db: Session, item):
    """Processa inserção"""
    dados = item.dados
    
    if item.tabela == "clientes":
        novo = Cliente(**dados)
        db.add(novo)
        
    elif item.tabela == "ordens_servico":
        novo = OrdemServico(**dados)
        db.add(novo)
        
    elif item.tabela == "lancamentos":
        novo = Lancamento(**dados)
        db.add(novo)

def _processar_update(db: Session, item):
    """Processa atualização"""
    dados = item.dados
    registro_id = item.registro_id
    
    if item.tabela == "clientes":
        registro = db.query(Cliente).filter(Cliente.id == registro_id).first()
        if registro:
            for chave, valor in dados.items():
                setattr(registro, chave, valor)
                
    elif item.tabela == "ordens_servico":
        registro = db.query(OrdemServico).filter(OrdemServico.id == registro_id).first()
        if registro:
            for chave, valor in dados.items():
                setattr(registro, chave, valor)
                
    elif item.tabela == "lancamentos":
        registro = db.query(Lancamento).filter(Lancamento.id == registro_id).first()
        if registro:
            for chave, valor in dados.items():
                setattr(registro, chave, valor)

def _processar_delete(db: Session, item):
    """Processa deleção"""
    registro_id = item.registro_id
    
    if item.tabela == "clientes":
        registro = db.query(Cliente).filter(Cliente.id == registro_id).first()
        if registro:
            db.delete(registro)
            
    elif item.tabela == "ordens_servico":
        registro = db.query(OrdemServico).filter(OrdemServico.id == registro_id).first()
        if registro:
            db.delete(registro)
            
    elif item.tabela == "lancamentos":
        registro = db.query(Lancamento).filter(Lancamento.id == registro_id).first()
        if registro:
            db.delete(registro)

@router.get("/status", response_model=dict)
async def status_sync(db: Session = Depends(get_db)):
    """Retorna status da fila de sincronização"""
    pendentes = db.query(SyncQueue).filter(SyncQueue.sincronizado == False).count()
    sincronizados = db.query(SyncQueue).filter(SyncQueue.sincronizado == True).count()
    
    return {
        "pendentes": pendentes,
        "sincronizados": sincronizados,
        "total": pendentes + sincronizados
    }
