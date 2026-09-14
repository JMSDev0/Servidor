from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FornecedorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_fornecedor: UUID
    nome: str
    cnpj: str
    telefone: str | None = None
    email: str | None = None
    criado_em: datetime | None = None
