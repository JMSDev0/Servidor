from uuid import UUID

from pydantic import BaseModel


class RelatorioMargemItem(BaseModel):
    id_produto: UUID
    nome: str
    preco_venda: float
    custo_medio: float | None = None
    margem_valor: float | None = None
    margem_percentual: float | None = None
    quantidade_estoque: int
    quantidade_fornecedores: int
