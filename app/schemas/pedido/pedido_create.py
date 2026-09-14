from pydantic import BaseModel, ConfigDict
from app.enums.pedido_enums import FormaPagamento
from uuid import UUID

class PedidoItemCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_produto: UUID
    quantidade: int

class PedidoCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    forma_pagamento: FormaPagamento
    itens: list[PedidoItemCreate]

    id_cliente: UUID | None = None

    id_empresa_contrato: UUID | None = None

    id_endereco_entrega: UUID | None = None

    itens: list[PedidoItemCreate]

    endereco_entrega_texto: str | None = None
