"""
Rotas de autenticação (login simples usuário/senha).
"""

import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario

router = APIRouter(tags=["Autenticação"])


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


class LoginRequest(BaseModel):
    usuario: str
    senha: str


class CriarUsuarioRequest(BaseModel):
    usuario: str
    senha: str
    nome: str = ""


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Valida usuário e senha."""
    user = db.query(Usuario).filter(Usuario.usuario == req.usuario, Usuario.ativo == True).first()
    if not user or user.senha_hash != hash_senha(req.senha):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha inválidos")

    return {
        "ok": True,
        "usuario": user.usuario,
        "nome": user.nome,
        # token simples (não é JWT; suficiente para o gate do frontend)
        "token": hash_senha(f"{user.usuario}:{user.senha_hash}"),
    }


@router.post("/usuarios")
def criar_usuario(req: CriarUsuarioRequest, db: Session = Depends(get_db)):
    """Cria um novo usuário."""
    if db.query(Usuario).filter(Usuario.usuario == req.usuario).first():
        raise HTTPException(status_code=400, detail="Usuário já existe")
    novo = Usuario(usuario=req.usuario, senha_hash=hash_senha(req.senha), nome=req.nome, ativo=True)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {"ok": True, "id": novo.id, "usuario": novo.usuario, "mensagem": "Usuário criado"}
