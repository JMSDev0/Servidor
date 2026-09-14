from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date
from app.enums.tipo_movimentacao import TipoMovimentacao

class MovimentacaoEstoqueCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_produto: UUID
    quantidade: int
    data_reposicao_prevista: date | None = None
    observacao: str | None = None
    id_fornecedor: UUID | None = None
    id_pedido: UUID | None = None
    tipo_movimentacao: TipoMovimentacao

