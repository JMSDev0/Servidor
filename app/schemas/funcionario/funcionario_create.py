from pydantic import BaseModel, ConfigDict
from datetime import date
from app.enums.tipo_funcionario import TipoFuncionario

class FuncionarioCreate(BaseModel):
    nome: str
    cpf: str
    email: str
    senha: str
    login: str
    telefone: str
    endereco: str
    data_nascimento: date | None

    salario: float
    tipo: TipoFuncionario
    comissao_percentual: float

    model_config = ConfigDict(from_attributes=True)
