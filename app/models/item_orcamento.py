from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum, INTEGER, DATE
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4

class ItemOrcamento(Base):
    __tablename__ = 'item_orcamento'
    id_item_orcamento = Column(UUID, primary_key=True, default=uuid4)
    quantidade = Column(INTEGER, nullable=False)
    # Nulo enquanto o item é sob_medida e ainda não foi precificado por um
    # funcionário (orçamento com status AGUARDANDO_PRECIFICACAO).
    preco_unitario = Column(DECIMAL(10,2), nullable=True)
    subtotal = Column(DECIMAL(10,2), nullable=True)

    id_orcamento = Column(UUID, ForeignKey('orcamento.id_orcamento'), nullable=False)
    orcamento = relationship("Orcamento", back_populates="itens", uselist=False)

    id_produto = Column(UUID, ForeignKey("produto.id_produto"), nullable=False)
    produto = relationship("Produto")
