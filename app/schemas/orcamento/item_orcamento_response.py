from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.schemas.produto.produto_response import ProdutoResponse

class ItemOrcamentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_item_orcamento: UUID
    id_produto: UUID
    quantidade: int
    preco_unitario: float | None
    subtotal: float | None
    produto: ProdutoResponse | None = None
