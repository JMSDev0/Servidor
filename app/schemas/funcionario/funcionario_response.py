from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from uuid import UUID

class FuncionarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_funcionario: UUID
    nome: str
    cpf: str
    email: str
    login: str
    telefone: str
    endereco: str
    data_nascimento: Optional[datetime] = None
    salario: float
    tipo: str
    comissao_percentual: Optional[float] = None
    ativo: bool
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
