from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum, INTEGER, DATE, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4
from app.enums.orcamento_enums import OrcamentoStatus

class Orcamento(Base):
    __tablename__ = 'orcamento'
    __table_args__ = (
        CheckConstraint("id_cliente IS NOT NULL OR id_empresa_contrato IS NOT NULL", name="ck_orcamento_cliente_ou_empresa"),
    )
    id_orcamento = Column(UUID, primary_key=True, default=uuid4)
    status = Column(Enum(OrcamentoStatus), default=OrcamentoStatus.PENDENTE, nullable=False)
    valor_total = Column(DECIMAL(10,2), nullable=False, default=0)
    data_validade = Column(DATE)
    criado_em = Column(TIMESTAMP, nullable=False, server_default=func.now())
    atualizado_em = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    id_cliente = Column(UUID, ForeignKey('cliente.id_cliente', ondelete="cascade"))
    cliente = relationship("Cliente", back_populates="orcamentos")

    id_funcionario = Column(UUID, ForeignKey('funcionario.id_funcionario', ondelete='set null'))
    funcionario = relationship("Funcionario")

    id_empresa_contrato = Column(UUID, ForeignKey('empresa_contrato.id_empresa_contrato', ondelete='set null'))
    empresa_contrato = relationship("EmpresaContrato")

    pedido = relationship("Pedido", back_populates="orcamento", uselist=False)

    itens = relationship("ItemOrcamento", back_populates="orcamento")
