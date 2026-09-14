from pydantic import BaseModel, ConfigDict
from app.enums.tipo_funcionario import TipoFuncionario
from datetime import date

class FuncionarioEdit(BaseModel):
    nome: str | None = None
    telefone: str | None = None
    endereco: str | None = None
    senha: str | None = None
    data_nascimento: date | None = None

    salario: float | None = None
    tipo: TipoFuncionario | None = None
    comissao_percentual: float | None = None

    model_config = ConfigDict(from_attributes=True)