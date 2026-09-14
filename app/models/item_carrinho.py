from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum, INTEGER, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4


class ItemCarrinho(Base):
    __tablename__ = 'item_carrinho'
    __table_args__ = (
        UniqueConstraint("id_carrinho", "id_produto", name="uq_item_carrinho_carrinho_produto"),
    )
    id_item_carrinho = Column(UUID, primary_key=True, default=uuid4)
    quantidade = Column(INTEGER, nullable=False)
    preco_unitario = Column(DECIMAL(10,2), nullable=False)

    id_carrinho = Column(UUID, ForeignKey("carrinho.id_carrinho"), nullable=False)
    carrinho = relationship("Carrinho", back_populates="itens", uselist=False)

    id_produto = Column(UUID, ForeignKey("produto.id_produto"), nullable=False)
    produto = relationship("Produto")
