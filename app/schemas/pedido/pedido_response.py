from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from uuid import UUID
from app.enums.pedido_enums import StatusPedido, FormaPagamento
from app.schemas.cliente.cliente_response import ClienteResponse
from app.schemas.produto.produto_response import ProdutoResponse

class ItemPedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_item_pedido: UUID
    id_produto: UUID
    produto: ProdutoResponse
    quantidade: int
    preco_unitario: float
    subtotal: float

class PedidoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_pedido: UUID
    status: StatusPedido
    forma_pagamento: FormaPagamento
    valor_frete: float
    valor_total: float
    data_pedido: datetime
    data_entrega_prevista: date | None = None
    data_entrega_realizada: date | None = None
    criado_em: datetime
    atualizado_em: datetime
    id_cliente: UUID | None = None
    id_empresa_contrato: UUID | None = None
    id_orcamento: UUID | None = None
    endereco_entrega_texto: str | None = None
    id_funcionario: UUID | None = None
    id_endereco_entrega: UUID | None = None
    itens: list[ItemPedidoResponse]
    cliente: ClienteResponse | None = None
