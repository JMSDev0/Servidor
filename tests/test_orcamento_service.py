"""
Testes UNITÁRIOS do OrcamentoService: chama o service direto em Python.
"""
import pytest

from app.enums.orcamento_enums import OrcamentoStatus
from app.enums.pedido_enums import FormaPagamento
from app.enums.tipo_producao import TipoProducao
from app.schemas.orcamento.orcamento_internal_save import OrcamentoInternalItemSave, OrcamentoInternalSave
from app.service.orcamento_service import OrcamentoService
from tests.helpers import criar_cliente, criar_funcionario, criar_produto, usuario_logado

orcamento_service = OrcamentoService()


def test_criar_orcamento_recalcula_valor_total(db_session):
    """RN-ORC-02: valor_total é recalculado pelo service a partir dos itens, nunca aceito cru."""
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, preco=40.0)

    orcamento = orcamento_service.save(
        OrcamentoInternalSave(
            id_cliente=cliente.id_cliente,
            itens=[OrcamentoInternalItemSave(id_produto=produto.id_produto, quantidade=3)],
        ),
        usuario_logado(funcionario),
        internal=True,
    )

    assert orcamento.valor_total == 120.0
    assert orcamento.status == OrcamentoStatus.PENDENTE
    assert orcamento.data_validade is not None


def test_criar_orcamento_sem_cliente_nem_empresa_falha(db_session):
    funcionario = criar_funcionario(db_session)
    produto = criar_produto(db_session)

    with pytest.raises(ValueError):
        orcamento_service.save(
            OrcamentoInternalSave(itens=[OrcamentoInternalItemSave(id_produto=produto.id_produto, quantidade=1)]),
            usuario_logado(funcionario),
            internal=True,
        )


def test_criar_orcamento_sob_medida_sem_preco_informado_falha(db_session):
    """RN-PRO-02: item sob_medida exige que o vendedor informe preco_unitario na hora de montar o orçamento interno."""
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, tipo_producao=TipoProducao.SOB_MEDIDA)

    with pytest.raises(ValueError):
        orcamento_service.save(
            OrcamentoInternalSave(
                id_cliente=cliente.id_cliente,
                itens=[OrcamentoInternalItemSave(id_produto=produto.id_produto, quantidade=1)],
            ),
            usuario_logado(funcionario),
            internal=True,
        )


def test_criar_orcamento_sob_medida_com_preco_informado_fica_pendente(db_session):
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, tipo_producao=TipoProducao.SOB_MEDIDA)

    orcamento = orcamento_service.save(
        OrcamentoInternalSave(
            id_cliente=cliente.id_cliente,
            itens=[OrcamentoInternalItemSave(id_produto=produto.id_produto, quantidade=2, preco_unitario=200.0)],
        ),
        usuario_logado(funcionario),
        internal=True,
    )

    assert orcamento.status == OrcamentoStatus.PENDENTE
    assert orcamento.valor_total == 400.0


def test_aprovar_orcamento_gera_pedido_vinculado(db_session):
    """RN-ORC-04/RN-PED-06: aprovar orçamento gera Pedido com id_orcamento apontando de volta pra ele."""
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, preco=40.0)

    orcamento = orcamento_service.save(
        OrcamentoInternalSave(
            id_cliente=cliente.id_cliente,
            itens=[OrcamentoInternalItemSave(id_produto=produto.id_produto, quantidade=2)],
        ),
        usuario_logado(funcionario),
        internal=True,
    )

    orcamento_service.change_status(
        orcamento.id_orcamento,
        OrcamentoStatus.APROVADO,
        usuario_logado(funcionario),
        internal=True,
        forma_pagamento=FormaPagamento.PIX,
        endereco_entrega_texto="Rua Teste, 123",
    )

    from app.repository.orcamento_repository import OrcamentoRepository
    from app.db.config import get_db_session

    with get_db_session() as db:
        orcamento_no_banco = OrcamentoRepository(db).get_orcamento_by_id(orcamento.id_orcamento)
        assert orcamento_no_banco.status == OrcamentoStatus.APROVADO
        assert orcamento_no_banco.pedido is not None
        assert orcamento_no_banco.pedido.id_orcamento == orcamento.id_orcamento
        assert orcamento_no_banco.pedido.valor_total == orcamento.valor_total


def test_aprovar_orcamento_ja_aprovado_falha(db_session):
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session)

    orcamento = orcamento_service.save(
        OrcamentoInternalSave(
            id_cliente=cliente.id_cliente,
            itens=[OrcamentoInternalItemSave(id_produto=produto.id_produto, quantidade=1)],
        ),
        usuario_logado(funcionario),
        internal=True,
    )
    orcamento_service.change_status(
        orcamento.id_orcamento, OrcamentoStatus.APROVADO, usuario_logado(funcionario),
        internal=True, forma_pagamento=FormaPagamento.PIX, endereco_entrega_texto="Rua Teste, 123",
    )

    with pytest.raises(ValueError):
        orcamento_service.change_status(
            orcamento.id_orcamento, OrcamentoStatus.APROVADO, usuario_logado(funcionario),
            internal=True, forma_pagamento=FormaPagamento.PIX, endereco_entrega_texto="Rua Teste, 123",
        )


def test_editar_itens_recalcula_subtotal_e_valor_total(db_session):
    """RN-IO-01: alterar itens do orçamento recalcula subtotal e, em cadeia, o valor_total."""
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, preco=10.0)

    orcamento = orcamento_service.save(
        OrcamentoInternalSave(
            id_cliente=cliente.id_cliente,
            itens=[OrcamentoInternalItemSave(id_produto=produto.id_produto, quantidade=1)],
        ),
        usuario_logado(funcionario),
        internal=True,
    )
    assert orcamento.valor_total == 10.0

    atualizado = orcamento_service.edit_itens_orcamento(
        orcamento.id_orcamento,
        [OrcamentoInternalItemSave(id_produto=produto.id_produto, quantidade=5)],
        usuario_logado(funcionario),
        internal=True,
    )

    assert atualizado.valor_total == 50.0
    assert len(atualizado.itens) == 1
    assert atualizado.itens[0].subtotal == 50.0
