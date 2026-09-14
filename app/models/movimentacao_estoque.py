from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum, INTEGER, DATE
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4
from app.enums.tipo_movimentacao import TipoMovimentacao

class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacao_estoque"
    id_movimentacao =  Column(UUID, primary_key=True, default=uuid4)
    tipo_movimentacao = Column(Enum(TipoMovimentacao), nullable=False)
    quantidade = Column(INTEGER, nullable=False)
    data_movimentacao = Column(TIMESTAMP, nullable=False, server_default=func.now())
    data_reposicao_prevista = Column(DATE)
    observacao = Column(VARCHAR(255))
    id_produto = Column(UUID, ForeignKey("produto.id_produto"), nullable=False)
    produto = relationship("Produto", back_populates="movimentacoes", uselist=False)
    id_fornecedor = Column(UUID, ForeignKey("fornecedor.id_fornecedor"), nullable=True)
    fornecedor = relationship("Fornecedor", uselist=False)
    id_pedido = Column(UUID, ForeignKey("pedido.id_pedido"), nullable=True)
    pedido = relationship("Pedido", uselist=False)
