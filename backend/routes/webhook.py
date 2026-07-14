"""
routes/webhook.py - Webhooks para integração com Node.js (Atendimento)

Recebe notificações quando:
- Senha é adicionada à OS
- Foto é enviada para OS
- Vídeo é enviado para OS
- Sincronização com servidor remoto completa
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import OrdemServico
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ===== WEBHOOK: Senha Adicionada =====

@router.post("/webhook/ordem/senha")
async def webhook_senha_adicionada(
    data: dict,
    db: Session = Depends(get_db)
):
    """
    Recebe notificação do Node.js quando senha é adicionada à OS

    Body esperado:
    {
        "numeroOS": 1,
        "senhaID": "pwd-abc123",
        "tipoSenha": "padrao",
        "criptografada": "hash..."
    }
    """
    try:
        numero_os = data.get("numeroOS")
        senha_id = data.get("senhaID")
        tipo_senha = data.get("tipoSenha", "padrao")

        if not numero_os or not senha_id:
            raise HTTPException(status_code=400, detail="numeroOS e senhaID são obrigatórios")

        ordem = db.query(OrdemServico).filter(OrdemServico.numero == numero_os).first()
        if not ordem:
            raise HTTPException(status_code=404, detail=f"OS número {numero_os} não encontrada")

        # Atualiza a ordem com informações da senha
        ordem.node_senha_id = senha_id
        ordem.senha_tipo = tipo_senha
        ordem.updated_at = datetime.utcnow()

        db.commit()

        logger.info(f"✅ Webhook: Senha adicionada à OS {numero_os}")

        return {"ok": True, "message": f"Senha da OS {numero_os} sincronizada"}

    except Exception as e:
        logger.error(f"❌ Webhook Senha: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== WEBHOOK: Foto Adicionada =====

@router.post("/webhook/ordem/foto")
async def webhook_foto_adicionada(
    data: dict,
    db: Session = Depends(get_db)
):
    """
    Recebe notificação do Node.js quando foto é adicionada à OS

    Body esperado:
    {
        "numeroOS": 1,
        "fotoID": "foto-abc123",
        "url": "http://localhost:3000/uploads/os-1/foto-abc123.jpg",
        "descricao": "Frente do telefone"
    }
    """
    try:
        numero_os = data.get("numeroOS")
        foto_id = data.get("fotoID")
        url = data.get("url", "")
        descricao = data.get("descricao", "")

        if not numero_os or not foto_id:
            raise HTTPException(status_code=400, detail="numeroOS e fotoID são obrigatórios")

        ordem = db.query(OrdemServico).filter(OrdemServico.numero == numero_os).first()
        if not ordem:
            raise HTTPException(status_code=404, detail=f"OS número {numero_os} não encontrada")

        # Inicializa array de fotos se vazio
        if not ordem.fotos:
            ordem.fotos = []

        # Adiciona nova foto
        foto_data = {
            "id": foto_id,
            "url": url,
            "descricao": descricao,
            "data": datetime.utcnow().isoformat()
        }
        ordem.fotos.append(foto_data)
        ordem.updated_at = datetime.utcnow()

        db.commit()

        logger.info(f"✅ Webhook: Foto adicionada à OS {numero_os}")

        return {"ok": True, "message": f"Foto {foto_id} sincronizada à OS {numero_os}"}

    except Exception as e:
        logger.error(f"❌ Webhook Foto: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== WEBHOOK: Vídeo Adicionado =====

@router.post("/webhook/ordem/video")
async def webhook_video_adicionado(
    data: dict,
    db: Session = Depends(get_db)
):
    """
    Recebe notificação do Node.js quando vídeo é adicionado à OS

    Body esperado:
    {
        "numeroOS": 1,
        "videoID": "video-abc123",
        "url": "http://localhost:3000/uploads/os-1/video-abc123.mp4",
        "duracao": 125,
        "descricao": "Diagnóstico inicial"
    }
    """
    try:
        numero_os = data.get("numeroOS")
        video_id = data.get("videoID")
        url = data.get("url", "")
        duracao = data.get("duracao", 0)
        descricao = data.get("descricao", "")

        if not numero_os or not video_id:
            raise HTTPException(status_code=400, detail="numeroOS e videoID são obrigatórios")

        ordem = db.query(OrdemServico).filter(OrdemServico.numero == numero_os).first()
        if not ordem:
            raise HTTPException(status_code=404, detail=f"OS número {numero_os} não encontrada")

        # Inicializa array de vídeos se vazio
        if not ordem.videos:
            ordem.videos = []

        # Adiciona novo vídeo
        video_data = {
            "id": video_id,
            "url": url,
            "duracao": duracao,
            "descricao": descricao,
            "data": datetime.utcnow().isoformat()
        }
        ordem.videos.append(video_data)
        ordem.updated_at = datetime.utcnow()

        db.commit()

        logger.info(f"✅ Webhook: Vídeo adicionado à OS {numero_os}")

        return {"ok": True, "message": f"Vídeo {video_id} sincronizado à OS {numero_os}"}

    except Exception as e:
        logger.error(f"❌ Webhook Vídeo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== WEBHOOK: Sincronização Completa =====

@router.post("/webhook/sync/completa")
async def webhook_sync_completa(
    data: dict,
    db: Session = Depends(get_db)
):
    """
    Recebe notificação quando sincronização com servidor remoto completa

    Body esperado:
    {
        "numeroOS": 1,
        "servidorID": "sp-001",
        "status": "sucesso",
        "timestamp": "2024-07-14T15:30:00"
    }
    """
    try:
        numero_os = data.get("numeroOS")
        servidor_id = data.get("servidorID")
        status = data.get("status", "sucesso")

        if not numero_os or not servidor_id:
            raise HTTPException(status_code=400, detail="numeroOS e servidorID são obrigatórios")

        ordem = db.query(OrdemServico).filter(OrdemServico.numero == numero_os).first()
        if not ordem:
            raise HTTPException(status_code=404, detail=f"OS número {numero_os} não encontrada")

        # Atualiza registro de sincronização
        if not ordem.sincronizado_com_servidores:
            ordem.sincronizado_com_servidores = {}

        ordem.sincronizado_com_servidores[servidor_id] = datetime.utcnow().isoformat()
        ordem.updated_at = datetime.utcnow()

        db.commit()

        logger.info(f"✅ Webhook: Sincronização de OS {numero_os} com {servidor_id} - {status}")

        return {"ok": True, "message": f"Sincronização registrada para OS {numero_os}"}

    except Exception as e:
        logger.error(f"❌ Webhook Sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== WEBHOOK: WhatsApp (Futuro) =====

@router.post("/webhook/whatsapp/mensagem")
async def webhook_whatsapp_mensagem(
    data: dict,
    db: Session = Depends(get_db)
):
    """
    Recebe mensagens do WhatsApp Business API

    Body esperado:
    {
        "entrada": "seu_numero",
        "numero_cliente": "5511999999999",
        "mensagem": "Qual é o status da minha OS?",
        "tipo": "texto"
    }
    """
    try:
        numero_cliente = data.get("numero_cliente")
        mensagem = data.get("mensagem")

        logger.info(f"📱 WhatsApp: Mensagem de {numero_cliente}: {mensagem}")

        # TODO: Implementar lógica de processamento de mensagens
        # - Extrair número da OS se mencionado
        # - Buscar status da OS
        # - Enviar resposta automática

        return {"ok": True, "message": "Mensagem recebida"}

    except Exception as e:
        logger.error(f"❌ Webhook WhatsApp: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== HEALTH CHECK DO WEBHOOK =====

@router.get("/webhook/health")
async def webhook_health():
    """Verifica se webhook está funcionando"""
    return {
        "status": "ok",
        "webhooks": [
            "ordem/senha",
            "ordem/foto",
            "ordem/video",
            "sync/completa",
            "whatsapp/mensagem"
        ]
    }
