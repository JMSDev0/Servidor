from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, func
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, DATE
from uuid import uuid4
from sqlalchemy.orm import relationship

class Cliente(Base):
    __tablename__ = "cliente"
    id_cliente = Column(UUID, primary_key=True, default=uuid4) 
    nome = Column(VARCHAR(120), nullable=False)
    cpf_cnpj = Column(VARCHAR(20), nullable=False, unique=True)
    email = Column(VARCHAR(150), nullable=False, unique=True)
    senha_hash = Column(VARCHAR(255), nullable=False)
    login = Column(VARCHAR(70), nullable=False, unique=True)
    telefone = Column(VARCHAR(20), nullable=False)
    data_nascimento = Column(DATE)
    ativo = Column(BOOLEAN, nullable=False, default=True)
    criado_em = Column(TIMESTAMP, nullable=False, server_default=func.now())
    atualizado_em = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    enderecos = relationship("EnderecoCliente", back_populates="cliente", cascade="all, delete-orphan")
    carrinhos = relationship("Carrinho", back_populates="cliente")
    orcamentos = relationship("Orcamento", back_populates="cliente")
    