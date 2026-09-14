from pydantic import BaseModel
from uuid import UUID


class ProdutoFornecedorAssociate(BaseModel):
    id_produto: UUID
    id_fornecedor: UUID
    preco_custo: float