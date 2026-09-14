from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum, INTEGER, DATE, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4
from app.enums.pedido_enums import StatusPedido, FormaPagamento

class Pedido(Base):
    __tablename__ = 'pedido'
    __table_args__ = (
        CheckConstraint("id_cliente IS NOT NULL OR id_empresa_contrato IS NOT NULL", name="ck_pedido_cliente_ou_empresa"),
        CheckConstraint("id_empresa_contrato IS NULL OR id_funcionario IS NOT NULL", name="ck_pedido_empresa_requer_funcionario"),
    )
    id_pedido = Column(UUID, primary_key=True, default=uuid4)
    status = Column(Enum(StatusPedido), nullable=False, default=StatusPedido.PENDENTE)
    forma_pagamento = Column(Enum(FormaPagamento), nullable=False)
    valor_frete = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    valor_total = Column(DECIMAL(10,2), nullable=False)
    data_pedido = Column(TIMESTAMP, nullable=False, server_default=func.now())
    data_entrega_prevista = Column(DATE)
    data_entrega_realizada = Column(DATE)
    criado_em = Column(TIMESTAMP, nullable=False, server_default=func.now())
    atualizado_em = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    id_cliente = Column(UUID, ForeignKey('cliente.id_cliente', ondelete="set null"), nullable=True)
    cliente = relationship("Cliente", uselist=False)

    id_empresa_contrato = Column(UUID, ForeignKey('empresa_contrato.id_empresa_contrato', ondelete="set null"), nullable=True)
    empresa_contrato = relationship("EmpresaContrato", uselist=False)

    id_orcamento = Column(UUID, ForeignKey('orcamento.id_orcamento', ondelete="set null"), nullable=True, unique=True)
    orcamento = relationship("Orcamento", back_populates="pedido", uselist=False)

    endereco_entrega_texto = Column(VARCHAR(255), nullable=True)

    id_funcionario = Column(UUID, ForeignKey('funcionario.id_funcionario', ondelete="set null"))
    funcionario = relationship("Funcionario", uselist=False)

    id_endereco_entrega = Column(UUID, ForeignKey('endereco_cliente.id_endereco', ondelete="set null"))
    endereco_entrega = relationship("EnderecoCliente", uselist=False)

    id_carrinho = Column(UUID, ForeignKey("carrinho.id_carrinho", ondelete="set null"))
    carrinho = relationship("Carrinho", uselist=False)

    itens = relationship("ItemPedido", back_populates="pedido")
