from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4

class EnderecoCliente(Base):
    __tablename__ = "endereco_cliente"
    id_endereco = Column(UUID, primary_key=True, default=uuid4)
    apelido = Column(VARCHAR(150))
    logradouro = Column(VARCHAR(150), nullable=False)
    numero = Column(VARCHAR(150))
    complemento = Column(VARCHAR(150))
    bairro = Column(VARCHAR(150), nullable=False)
    cidade = Column(VARCHAR(150), nullable=False)
    estado = Column(VARCHAR(150), nullable=False)
    cep = Column(VARCHAR(150), nullable=False)
    principal = Column(BOOLEAN, nullable=False, default=False)
    criado_em = Column(TIMESTAMP, nullable=False, server_default=func.now())
     
    id_cliente = Column(UUID, ForeignKey("cliente.id_cliente"), nullable=False) 
    cliente = relationship("Cliente", back_populates="enderecos", uselist=False)
    