from pydantic import BaseModel, ConfigDict
from uuid import UUID

class EnderecoCliente(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    apelido: str | None = None
    logradouro: str
    numero: str | None = None
    complemento: str | None = None
    bairro: str
    cidade: str
    estado: str
    cep: str
    principal: bool | None = False

    id_cliente: UUID | None = None