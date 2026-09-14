from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EmpresaContratoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_empresa_contrato: UUID
    nome: str
    cnpj: str
    telefone: str | None = None
    email: str | None = None
    info_contrato: str | None = None
    data_inicio: date
    data_fim: date | None = None
    contrato_ativo: bool
    criado_em: datetime | None = None
