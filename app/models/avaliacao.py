from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum, INTEGER, DATE
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4

class Avaliacao(Base):
    __tablename__ = 'avaliacao'
    id_avaliacao = Column(UUID, primary_key=True, default=uuid4)
    nota = Column(INTEGER, nullable=False)
    comentario = Column(VARCHAR(800))
    criado_em = Column(TIMESTAMP, nullable=False, server_default=func.now())

    id_pedido = Column(UUID, ForeignKey("pedido.id_pedido", ondelete="set null"))
    pedido = relationship("Pedido", uselist=False)

    id_produto = Column(UUID, ForeignKey("produto.id_produto"), nullable=False)
    produto = relationship("Produto", back_populates="avaliacoes")

    id_cliente = Column(UUID, ForeignKey("cliente.id_cliente"), nullable=False)
    cliente = relationship("Cliente")
