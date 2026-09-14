from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum, INTEGER
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4

class ProdutoFornecedor(Base):
    __tablename__ = "produto_fornecedor"

    id_produto_fornecedor = Column(UUID, primary_key=True, default=uuid4)
    preco_custo = Column(DECIMAL(10,2), nullable=False)

    id_produto = Column(UUID, ForeignKey("produto.id_produto", ondelete="CASCADE"), nullable=False, )
    produto = relationship("Produto", back_populates="fornecedores")

    id_fornecedor = Column(UUID, ForeignKey("fornecedor.id_fornecedor", ondelete="CASCADE"), nullable=False)
    fornecedor = relationship("Fornecedor", back_populates="produtos")
    