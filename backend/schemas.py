"""
schemas.py - Pydantic models para validação de request/response
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime

# ===== CLIENTE =====
class ClienteBase(BaseModel):
    codigo: int
    nome: str = Field(..., min_length=1, max_length=120)
    endereco: Optional[str] = Field(None, max_length=150)
    cidade: Optional[str] = Field(None, max_length=80)
    cep: Optional[str] = Field(None, max_length=10)
    telefone: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = Field(None, max_length=120)
    contato: Optional[str] = Field(None, max_length=60)
    ativo: bool = True

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    cep: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    contato: Optional[str] = None
    ativo: Optional[bool] = None

class ClienteResponse(ClienteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== ORDEM ITEM =====
class OrdemItemBase(BaseModel):
    descricao: str = Field(..., min_length=1, max_length=255)
    quantidade: float = Field(1.0, gt=0)
    valor_unitario: float = Field(0.0, ge=0)
    valor_total: float = Field(0.0, ge=0)

class OrdemItemCreate(OrdemItemBase):
    pass

class OrdemItemResponse(OrdemItemBase):
    id: int
    ordem_id: int
    
    class Config:
        from_attributes = True

# ===== ORDEM DE SERVIÇO =====
class OrdemServicioBase(BaseModel):
    numero: int
    cliente_id: int
    descricao: Optional[str] = None
    data_abertura: date
    data_fechamento: Optional[date] = None
    status: str = "aberto"
    tecnico: Optional[str] = Field(None, max_length=60)
    observacoes: Optional[str] = None

class OrdemServicioCreate(OrdemServicioBase):
    pass

class OrdemServicioUpdate(BaseModel):
    descricao: Optional[str] = None
    data_fechamento: Optional[date] = None
    status: Optional[str] = None
    tecnico: Optional[str] = None
    observacoes: Optional[str] = None

class OrdemServicioResponse(OrdemServicioBase):
    id: int
    valor_total: float
    itens: List[OrdemItemResponse] = []
    cliente: ClienteResponse
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== LANCAMENTO (Financeiro) =====
class LancamentoBase(BaseModel):
    data: date
    tipo: str = Field(..., pattern="^(receita|despesa)$")
    categoria: Optional[str] = Field(None, max_length=60)
    descricao: Optional[str] = Field(None, max_length=255)
    valor: float = Field(..., gt=0)
    forma_pagamento: Optional[str] = Field(None, max_length=30)
    numero_recibo: Optional[str] = Field(None, max_length=20)
    cliente_id: Optional[int] = None
    ordem_id: Optional[int] = None

class LancamentoCreate(LancamentoBase):
    pass

class LancamentoUpdate(BaseModel):
    data: Optional[date] = None
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    valor: Optional[float] = None
    forma_pagamento: Optional[str] = None
    numero_recibo: Optional[str] = None
    baixado: Optional[bool] = None

class LancamentoResponse(LancamentoBase):
    id: int
    baixado: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== SYNC =====
class SyncQueueItem(BaseModel):
    tabela: str
    operacao: str
    registro_id: int
    dados: dict

class SyncRequest(BaseModel):
    itens: List[SyncQueueItem]
    timestamp: datetime

class SyncResponse(BaseModel):
    status: str  # success, conflict, error
    sincronizados: int
    conflitos: int
    erros: List[str] = []

# ===== RESPONSE GENÉRICA =====
class MessageResponse(BaseModel):
    message: str
    status: str = "success"

class ErrorResponse(BaseModel):
    message: str
    status: str = "error"
    detail: Optional[str] = None
