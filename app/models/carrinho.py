from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum, INTEGER
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4
from app.enums.status_carrinho import StatusCarrinho

class Carrinho(Base):
    __tablename__ = 'carrinho'
    id_carrinho = Column(UUID, primary_key=True, default=uuid4)
    status = Column(Enum(StatusCarrinho), nullable=False, default=StatusCarrinho.ABERTO)
    criado_em = Column(TIMESTAMP, nullable=False, server_default=func.now())
    atualizado_em = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    id_cliente = Column(UUID, ForeignKey("cliente.id_cliente"))
    cliente = relationship("Cliente", back_populates="carrinhos", uselist=False)
    itens = relationship("ItemCarrinho", back_populates="carrinho")
    