from pydantic import BaseModel

class PrimeiroAcessoSolicitar(BaseModel):
    cpf_cnpj: str
    email: str
