"""
seed.py - Dados iniciais (exemplo) para o sistema não ficar zerado.
Cria um cliente e uma OS de exemplo se as tabelas estiverem vazias.
Idempotente: só cria se não existir nada.
"""

import logging
from datetime import datetime, date

from database import SessionLocal
from models import Cliente, OrdemServico, Lancamento

logger = logging.getLogger(__name__)


def seed_dados_iniciais():
    """Popula dados de exemplo se o banco estiver vazio."""
    db = SessionLocal()
    try:
        # ===== CLIENTE EXEMPLO =====
        cliente = db.query(Cliente).first()
        if not cliente:
            cliente = Cliente(
                codigo=1,
                nome="Cliente Exemplo",
                endereco="Rua das Flores, 123",
                cidade="São Paulo",
                cep="01000-000",
                telefone="11 99999-9999",
                email="cliente@exemplo.com",
                contato="Contato Exemplo",
                ativo=True,
            )
            db.add(cliente)
            db.commit()
            db.refresh(cliente)
            logger.info(f"🌱 Cliente exemplo criado (id={cliente.id})")

        # ===== OS EXEMPLO =====
        ordem = db.query(OrdemServico).first()
        if not ordem:
            numero_os = f"OS-{datetime.now().strftime('%Y%m%d')}-00001"
            ordem = OrdemServico(
                numero=1,
                numero_os=numero_os,
                cliente_id=cliente.id,
                status="aberta",
                data_abertura=date.today(),
                data_criacao=datetime.now(),
                tecnico="Técnico Exemplo",
                # Produto
                produto_tipo="celular",
                marca="Samsung",
                modelo="Galaxy S21",
                imei="356938035643809",
                # Endereço / contato
                endereco_rua="Rua das Flores",
                endereco_tipo="casa",
                endereco_numero="123",
                bairro="Centro",
                cidade_os="São Paulo",
                telefone_contato="11 99999-9999",
                # Problema
                problema_descricao="Tela trincada e bateria viciando (exemplo).",
                valor_total=0.0,
            )
            db.add(ordem)
            db.commit()
            db.refresh(ordem)
            logger.info(f"🌱 OS exemplo criada ({ordem.numero_os}, id={ordem.id})")

        # ===== LANÇAMENTO FINANCEIRO EXEMPLO =====
        lancamento = db.query(Lancamento).first()
        if not lancamento:
            lancamento = Lancamento(
                data=date.today(),
                tipo="receita",
                categoria="Serviço",
                descricao="Lançamento exemplo (troca de tela)",
                valor=150.0,
                cliente_id=cliente.id,
                ordem_id=ordem.id,
                forma_pagamento="dinheiro",
                baixado=False,
            )
            db.add(lancamento)
            db.commit()
            logger.info("🌱 Lançamento financeiro exemplo criado")

        logger.info("✅ Seed de dados iniciais concluído")

    except Exception as e:
        db.rollback()
        logger.warning(f"⚠️  Seed ignorado (possível dado já existente): {e}")
    finally:
        db.close()
