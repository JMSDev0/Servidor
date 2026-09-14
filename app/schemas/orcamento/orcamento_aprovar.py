from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.enums.pedido_enums import FormaPagamento

class OrcamentoAprovar(BaseModel):
    """
    Só é obrigatório de fato preencher isso quando new_status=aprovado.
    Pra qualquer outro status (cancelado, expirado, aguardando_precificacao),
    pode mandar o corpo vazio {} — o service ignora esses campos nesse caso.
    """
    model_config = ConfigDict(from_attributes=True)
    forma_pagamento: FormaPagamento | None = None
    id_endereco_entrega: UUID | None = None
    endereco_entrega_texto: str | None = None
