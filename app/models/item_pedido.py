from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum, INTEGER, DATE
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4

class ItemPedido(Base):
    __tablename__ = 'item_pedido'
    id_item_pedido = Column(UUID, primary_key=True, default=uuid4)
    quantidade = Column(INTEGER, nullable=False)
    preco_unitario = Column(DECIMAL(10,2), nullable=False)
    subtotal = Column(DECIMAL(10,2), nullable=False)

    id_pedido = Column(UUID, ForeignKey("pedido.id_pedido"), nullable=False)
    pedido = relationship("Pedido", back_populates="itens", uselist=False)

    id_produto = Column(UUID, ForeignKey("produto.id_produto"), nullable=False)
    produto = relationship("Produto", uselist=False)
