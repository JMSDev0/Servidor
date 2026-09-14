"""
Testes UNITÁRIOS do PedidoService: chama o service direto em Python.
"""
import pytest

from app.db.config import get_db_session
from app.enums.pedido_enums import FormaPagamento, StatusPedido
from app.enums.tipo_producao import TipoProducao
from app.models.produto import Produto
from app.schemas.pedido.pedido_create import PedidoCreate, PedidoItemCreate
from app.service.pedido_service import PedidoService
from tests.helpers import criar_cliente, criar_funcionario, criar_produto, usuario_logado

pedido_service = PedidoService()


def buscar_quantidade_estoque(id_produto):
    """Consulta numa sessão nova (não a `db_session` do teste, que já tem o
    produto na identity map de antes do pedido) -- pedido_service.save roda
    em sessões próprias, então reconsultar pela `db_session` do teste pode
    devolver o objeto em cache em vez do estado já commitado por elas."""
    with get_db_session() as db:
        return db.query(Produto).filter(Produto.id_produto == id_produto).first().quantidade_estoque


def pedido_com_item(id_cliente, id_produto, quantidade=2):
    return PedidoCreate(
        forma_pagamento=FormaPagamento.PIX,
        itens=[PedidoItemCreate(id_produto=id_produto, quantidade=quantidade)],
        id_cliente=id_cliente,
        endereco_entrega_texto="Rua Teste, 123",
    )


def test_criar_pedido_baixa_estoque(db_session):
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, preco=50.0, quantidade_estoque=10)

    pedido = pedido_service.save(
        pedido_com_item(cliente.id_cliente, produto.id_produto, quantidade=3),
        usuario_logado(funcionario),
        internal=True,
    )

    assert pedido.valor_total == 150.0
    assert buscar_quantidade_estoque(produto.id_produto) == 7


def test_criar_pedido_sem_cliente_nem_empresa_falha(db_session):
    funcionario = criar_funcionario(db_session)
    produto = criar_produto(db_session)

    dados = PedidoCreate(
        forma_pagamento=FormaPagamento.PIX,
        itens=[PedidoItemCreate(id_produto=produto.id_produto, quantidade=1)],
        endereco_entrega_texto="Rua Teste, 123",
    )

    with pytest.raises(ValueError):
        pedido_service.save(dados, usuario_logado(funcionario), internal=True)


def test_criar_pedido_com_produto_sob_medida_falha(db_session):
    """Produto sob_medida não pode ir direto pra pedido -- precisa de orçamento antes."""
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, tipo_producao=TipoProducao.SOB_MEDIDA)

    with pytest.raises(ValueError):
        pedido_service.save(
            pedido_com_item(cliente.id_cliente, produto.id_produto), usuario_logado(funcionario), internal=True
        )


def test_criar_pedido_com_estoque_insuficiente_falha(db_session):
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, quantidade_estoque=1)

    with pytest.raises(ValueError):
        pedido_service.save(
            pedido_com_item(cliente.id_cliente, produto.id_produto, quantidade=5),
            usuario_logado(funcionario),
            internal=True,
        )


def test_transicao_de_status_valida_funciona(db_session):
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, quantidade_estoque=10)
    pedido = pedido_service.save(
        pedido_com_item(cliente.id_cliente, produto.id_produto), usuario_logado(funcionario), internal=True
    )

    atualizado = pedido_service.update_status(pedido.id_pedido, StatusPedido.PAGO, usuario_logado(funcionario))

    assert atualizado.status == StatusPedido.PAGO


def test_transicao_de_status_invalida_falha(db_session):
    """RN-PED-02: não dá pra ir de pendente direto pra entregue."""
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, quantidade_estoque=10)
    pedido = pedido_service.save(
        pedido_com_item(cliente.id_cliente, produto.id_produto), usuario_logado(funcionario), internal=True
    )

    with pytest.raises(ValueError):
        pedido_service.update_status(pedido.id_pedido, StatusPedido.ENTREGUE, usuario_logado(funcionario))


def test_cancelar_pedido_devolve_estoque(db_session):
    """RN-PED-03: cancelar gera movimentação de entrada devolvendo a quantidade."""
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, quantidade_estoque=10)
    pedido = pedido_service.save(
        pedido_com_item(cliente.id_cliente, produto.id_produto, quantidade=4),
        usuario_logado(funcionario),
        internal=True,
    )
    assert buscar_quantidade_estoque(produto.id_produto) == 6

    pedido_service.update_status(pedido.id_pedido, StatusPedido.CANCELADO, usuario_logado(funcionario))

    assert buscar_quantidade_estoque(produto.id_produto) == 10


def test_buscar_pedidos_por_cliente(db_session):
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, quantidade_estoque=10)
    pedido_service.save(
        pedido_com_item(cliente.id_cliente, produto.id_produto), usuario_logado(funcionario), internal=True
    )

    pedidos = pedido_service.get_by_cliente(
        id_cliente=cliente.id_cliente, current_user=usuario_logado(funcionario), internal=True
    )

    assert len(pedidos) == 1
