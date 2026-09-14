from pydantic import BaseModel

class PrimeiroAcessoConfirmar(BaseModel):
    token: str
    senha: str
