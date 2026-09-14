from enum import Enum

class StatusPedido(Enum):
    PENDENTE = 'pendente'
    PAGO = 'pago'
    EM_SEPARACAO = 'em_separacao'
    ENVIADO = 'enviado'
    ENTREGUE = 'entregue'
    CANCELADO = 'cancelado'

class FormaPagamento(Enum):
    DEBITO = 'debito'
    CREDITO = 'credito'
    DINHEIRO = 'dinheiro'
    PIX = 'pix'
