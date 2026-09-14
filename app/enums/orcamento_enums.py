from enum import Enum

class OrcamentoStatus(Enum):
    AGUARDANDO_PRECIFICACAO = 'aguardando_precificacao'
    PENDENTE = 'pendente'
    APROVADO = 'aprovado'
    CANCELADO = 'cancelado'
    EXPIRADO = 'expirado'
