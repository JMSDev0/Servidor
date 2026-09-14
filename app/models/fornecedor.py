from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4

class Fornecedor(Base):
    __tablename__ = "fornecedor"
    id_fornecedor = Column(UUID, primary_key=True, default=uuid4)
    nome = Column(VARCHAR(150), nullable=False)
    cnpj = Column(VARCHAR(20), nullable=False, unique=True)
    telefone = Column(VARCHAR(150), unique=True)
    email = Column(VARCHAR(150), unique=True)
    criado_em = Column(TIMESTAMP, nullable=False, server_default=func.now())
    produtos = relationship("ProdutoFornecedor", back_populates="fornecedor", cascade="all, delete-orphan")
    