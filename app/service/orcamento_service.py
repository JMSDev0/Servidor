from app.db.config import get_db_session
from app.repository.orcamento_repository import OrcamentoRepository
from app.repository.produto_repository import ProdutoRepository
from app.service.auth_service import check_user_permission, get_current_cliente
from app.schemas.orcamento.orcamento_internal_save import OrcamentoInternalSave, OrcamentoInternalItemSave
from app.models.orcamento import Orcamento
from app.models.item_orcamento import ItemOrcamento
from app.service.cliente_service import ClienteService
from app.service.pedido_service import PedidoService
from app.enums.orcamento_enums import OrcamentoStatus
from app.enums.tipo_producao import TipoProducao
from app.exceptions.exceptions import UnauthorizedException
from app.schemas.orcamento.orcamento_response import OrcamentoResponse
from app.schemas.page_model import PageModel
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID

DIAS_VALIDADE_ORCAMENTO = 15

class OrcamentoService:
    def __init__(self):
        pass

    def _to_decimal(self, value):
        """
        preco_unitario chega dos schemas como float (Pydantic), mas a coluna
        no banco é DECIMAL — o SQLAlchemy devolve decimal.Decimal pra tudo que
        já veio do banco (ex: produto.preco). Sem essa conversão, dá pra
        acabar com um item_orcamento.subtotal em Decimal e outro em float no
        mesmo orçamento, e o sum() deles explode com
        "unsupported operand type(s) for +: 'decimal.Decimal' and 'float'".
        Passar por str() evita o problema de precisão binária de criar um
        Decimal direto a partir de um float.
        """
        if value is None:
            return None
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    def _resolve_preco_unitario(self, produto, item, internal):
        """
        Produto pronto: sempre usa o preço de catálogo do produto.
        Produto sob_medida criado por um funcionário (internal=True): exige
        que o preco_unitario venha informado no item — é o vendedor quem
        decide o valor, não existe preço de tabela pra algo feito sob medida.
        Produto sob_medida pedido pelo cliente no self-service: não tem como
        precificar na hora — devolve None de propósito, e quem chama (save /
        edit_itens_orcamento) deixa o orçamento em AGUARDANDO_PRECIFICACAO até
        um funcionário definir o valor pelo definir_preco_item.
        """
        if produto.tipo_producao != TipoProducao.SOB_MEDIDA:
            return produto.preco

        if not internal:
            return None

        if item.preco_unitario is None:
            raise ValueError(
                f"Informe o valor do item sob medida para o produto '{produto.nome}'."
            )
        return self._to_decimal(item.preco_unitario)

    def _aplicar_status_por_precificacao(self, orcamento_data, itens_orcamento):
        """
        Depois de resolver os itens, decide se o orçamento já pode seguir
        pra PENDENTE (com a validade começando a contar) ou se precisa
        esperar um funcionário precificar algum item sob_medida pendente.
        """
        aguardando = any(item.preco_unitario is None for item in itens_orcamento)
        orcamento_data.valor_total = sum(
            item.subtotal for item in itens_orcamento if item.subtotal is not None
        )
        if aguardando:
            orcamento_data.status = OrcamentoStatus.AGUARDANDO_PRECIFICACAO
            orcamento_data.data_validade = None
        else:
            orcamento_data.status = OrcamentoStatus.PENDENTE
            orcamento_data.data_validade = date.today() + timedelta(days=DIAS_VALIDADE_ORCAMENTO)
        return orcamento_data

    def get_orcamento_by_id(self, id_orcamento):
        with get_db_session() as db:
            orcamento_repo = OrcamentoRepository(db)
            return orcamento_repo.get_orcamento_by_id(id_orcamento)

    def get_orcamento_by_id_internal(self, id_orcamento, current_user):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            orcamento_repo = OrcamentoRepository(db)
            orcamento = orcamento_repo.get_orcamento_by_id(id_orcamento)
            if not orcamento:
                raise ValueError("Orçamento não encontrado")
            return OrcamentoResponse.model_validate(orcamento)

    def listar_aguardando_precificacao(self, current_user):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            orcamento_repo = OrcamentoRepository(db)
            orcamentos = orcamento_repo.list_by_status(OrcamentoStatus.AGUARDANDO_PRECIFICACAO)
            return [OrcamentoResponse.model_validate(orcamento) for orcamento in orcamentos]

    def find(self, page: int, size: int, status: OrcamentoStatus | None, current_user, id_cliente=None, cliente=None):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            orcamento_repo = OrcamentoRepository(db)
            orcamentos = orcamento_repo.find_paginated(page, size, status, id_cliente, cliente)
            total = orcamento_repo.count(status, id_cliente, cliente)
            return PageModel(
                content=[OrcamentoResponse.model_validate(orcamento) for orcamento in orcamentos],
                page=page,
                size=size,
                total_pages=(total + size - 1) // size if size else 0,
                total_items=total,
            )

    def get_orcamento_by_id_self_service(self, id_orcamento, current_user):
        cliente = get_current_cliente(current_user)
        with get_db_session() as db:
            orcamento_repo = OrcamentoRepository(db)
            orcamento = orcamento_repo.get_orcamento_by_id(id_orcamento)
            if not orcamento:
                raise ValueError("Orçamento não encontrado")
            if orcamento.id_cliente != cliente.id_cliente:
                raise UnauthorizedException("Acesso não autorizado a este orçamento")
            return OrcamentoResponse.model_validate(orcamento)

    def save(self, orcamento: OrcamentoInternalSave, current_user: dict, internal=False):
        orcamento_data = Orcamento()
        if internal:
            func = check_user_permission(current_user, repo="funcionario")
            orcamento_data.id_funcionario = func.id_funcionario
            if orcamento.id_cliente:
                cliente_service = ClienteService()
                cliente = cliente_service.get_by_id(orcamento.id_cliente)
                if not cliente:
                    raise ValueError("Cliente não encontrado")
                orcamento_data.id_cliente = orcamento.id_cliente
            elif orcamento.id_empresa_contrato:
                orcamento_data.id_empresa_contrato = orcamento.id_empresa_contrato
            else:
                raise ValueError("É necessário informar o id_cliente ou id_empresa_contrato")
        else:
            cliente = get_current_cliente(current_user)
            orcamento_data.id_cliente = cliente.id_cliente

        with get_db_session() as db:
            orcamento_repo = OrcamentoRepository(db)
            orcamento_data = orcamento_repo.save(orcamento_data)
            itens_criados = []
            for item in orcamento.itens:
                item_orcamento = ItemOrcamento()
                item_orcamento.id_orcamento = orcamento_data.id_orcamento
                item_orcamento.quantidade = item.quantidade
                # Reaproveita a sessão `db` já aberta neste método (em vez de
                # ProdutoService().get_by_id(), que abriria outra sessão) --
                # evita que o header do orçamento, já inserido nesta mesma
                # transação mas ainda não commitado, fique vulnerável a uma
                # sessão aninhada fechando e revertendo o que ainda não foi
                # commitado (some SQLite in-memory de teste compartilha uma
                # única conexão entre sessões, então isso já causou um
                # rollback silencioso do orçamento no meio da criação).
                produto = ProdutoRepository(db).get_by_id(item.id_produto)
                if not produto:
                    raise ValueError(f"Produto com id {item.id_produto} não encontrado")
                item_orcamento.id_produto = item.id_produto
                item_orcamento.preco_unitario = self._resolve_preco_unitario(produto, item, internal)
                item_orcamento.subtotal = (
                    item_orcamento.quantidade * item_orcamento.preco_unitario
                    if item_orcamento.preco_unitario is not None else None
                )
                orcamento_repo.save_item_orcamento(item_orcamento)
                itens_criados.append(item_orcamento)
            self._aplicar_status_por_precificacao(orcamento_data, itens_criados)
            db.commit()
            return OrcamentoResponse.model_validate(orcamento_data)

    def edit_itens_orcamento(self, id_orcamento, itens: list[OrcamentoInternalItemSave], current_user: dict, internal=False):
        cliente = None
        if internal:
            check_user_permission(current_user, repo="funcionario")
        else:
            cliente = get_current_cliente(current_user)
        with get_db_session() as db:
            orcamento_repo = OrcamentoRepository(db)
            orcamento = orcamento_repo.get_orcamento_by_id(id_orcamento)
            if not orcamento:
                raise ValueError("Orçamento não encontrado")
            if not internal and orcamento.id_cliente != cliente.id_cliente:
                raise UnauthorizedException("Acesso não autorizado a este orçamento")
            if orcamento.status not in [OrcamentoStatus.PENDENTE, OrcamentoStatus.AGUARDANDO_PRECIFICACAO]:
                raise ValueError("Apenas orçamentos pendentes ou aguardando precificação podem ser editados")
            for item in orcamento.itens:
                db.delete(item)
            db.flush()
            itens_criados = []
            for item in itens:
                item_orcamento = ItemOrcamento()
                item_orcamento.id_orcamento = id_orcamento
                item_orcamento.quantidade = item.quantidade
                # Reaproveita a sessão `db` já aberta neste método (em vez de
                # ProdutoService().get_by_id(), que abriria outra sessão) --
                # evita que o header do orçamento, já inserido nesta mesma
                # transação mas ainda não commitado, fique vulnerável a uma
                # sessão aninhada fechando e revertendo o que ainda não foi
                # commitado (some SQLite in-memory de teste compartilha uma
                # única conexão entre sessões, então isso já causou um
                # rollback silencioso do orçamento no meio da criação).
                produto = ProdutoRepository(db).get_by_id(item.id_produto)
                if not produto:
                    raise ValueError(f"Produto com id {item.id_produto} não encontrado")
                item_orcamento.id_produto = item.id_produto
                item_orcamento.preco_unitario = self._resolve_preco_unitario(produto, item, internal)
                item_orcamento.subtotal = (
                    item_orcamento.quantidade * item_orcamento.preco_unitario
                    if item_orcamento.preco_unitario is not None else None
                )
                orcamento_repo.save_item_orcamento(item_orcamento)
                itens_criados.append(item_orcamento)
            self._aplicar_status_por_precificacao(orcamento, itens_criados)
            orcamento.atualizado_em = datetime.now()
            db.commit()
            return OrcamentoResponse.model_validate(orcamento)

    def definir_preco_item(self, id_orcamento, id_item_orcamento, preco_unitario, current_user):
        """
        Usado pelo funcionário/vendedor pra preencher o valor de um item
        sob_medida que ficou pendente de precificação (item criado pelo
        cliente no self-service, com preco_unitario nulo). Quando todos os
        itens do orçamento já tiverem preço, ele sai de
        AGUARDANDO_PRECIFICACAO e vira PENDENTE — é nesse momento que a
        validade do orçamento começa a contar, não antes.
        """
        check_user_permission(current_user, repo="funcionario")
        # `item.id_item_orcamento` (carregado do banco) é sempre um uuid.UUID
        # de verdade; normaliza aqui pra aceitar tanto UUID quanto str (ex.:
        # quem chama via HTTP já recebe UUID por causa da tipagem da rota,
        # mas quem chama o service direto pode passar string) -- comparar
        # UUID com str sempre dá False em Python, então sem isso o item
        # nunca é encontrado.
        if isinstance(id_item_orcamento, str):
            id_item_orcamento = UUID(id_item_orcamento)
        with get_db_session() as db:
            orcamento_repo = OrcamentoRepository(db)
            orcamento = orcamento_repo.get_orcamento_by_id(id_orcamento)
            if not orcamento:
                raise ValueError("Orçamento não encontrado")
            if orcamento.status != OrcamentoStatus.AGUARDANDO_PRECIFICACAO:
                raise ValueError("Este orçamento não está aguardando precificação")

            item_orcamento = next(
                (item for item in orcamento.itens if item.id_item_orcamento == id_item_orcamento),
                None,
            )
            if not item_orcamento:
                raise ValueError("Item do orçamento não encontrado")

            preco_unitario = self._to_decimal(preco_unitario)
            item_orcamento.preco_unitario = preco_unitario
            item_orcamento.subtotal = item_orcamento.quantidade * preco_unitario

            if all(item.preco_unitario is not None for item in orcamento.itens):
                orcamento.status = OrcamentoStatus.PENDENTE
                orcamento.data_validade = date.today() + timedelta(days=DIAS_VALIDADE_ORCAMENTO)
                orcamento.valor_total = sum(item.subtotal for item in orcamento.itens)

            orcamento.atualizado_em = datetime.now()
            db.commit()
            return OrcamentoResponse.model_validate(orcamento)

    def change_status(self, id_orcamento, new_status: OrcamentoStatus, current_user, internal=True,
                       forma_pagamento=None, id_endereco_entrega=None, endereco_entrega_texto=None):
        with get_db_session() as db:
            orcamento_repo = OrcamentoRepository(db)
            orcamento = orcamento_repo.get_orcamento_by_id(id_orcamento)
            if not orcamento:
                raise ValueError("Orçamento não encontrado")

            if internal:
                check_user_permission(current_user, repo="funcionario")
            else:
                cliente = get_current_cliente(current_user)
                if orcamento.id_cliente != cliente.id_cliente:
                    raise UnauthorizedException("Acesso não autorizado a este orçamento")
                if new_status != OrcamentoStatus.CANCELADO:
                    raise UnauthorizedException("Cliente só pode cancelar o próprio orçamento")
                if orcamento.status not in [OrcamentoStatus.PENDENTE, OrcamentoStatus.AGUARDANDO_PRECIFICACAO]:
                    raise ValueError("Apenas orçamentos pendentes ou aguardando precificação podem ser cancelados pelo cliente")

            if new_status == OrcamentoStatus.APROVADO and orcamento.status != OrcamentoStatus.PENDENTE:
                raise ValueError("Apenas orçamentos pendentes podem ser aprovados")
            if new_status == OrcamentoStatus.CANCELADO and orcamento.status not in [OrcamentoStatus.PENDENTE, OrcamentoStatus.APROVADO, OrcamentoStatus.AGUARDANDO_PRECIFICACAO]:
                raise ValueError("Apenas orçamentos pendentes, aprovados ou aguardando precificação podem ser cancelados")
            if new_status == OrcamentoStatus.EXPIRADO and orcamento.status != OrcamentoStatus.PENDENTE:
                raise ValueError("Apenas orçamentos pendentes podem expirar")

            if new_status == OrcamentoStatus.APROVADO:
                if forma_pagamento is None:
                    raise ValueError("Informe a forma de pagamento para aprovar o orçamento.")
                if id_endereco_entrega is None and endereco_entrega_texto is None:
                    raise ValueError("Informe o endereço de entrega (id_endereco_entrega ou endereco_entrega_texto) para aprovar o orçamento.")
                pedido_service = PedidoService()
                pedido_service.save_from_orcamento(orcamento, forma_pagamento, id_endereco_entrega, endereco_entrega_texto)

            orcamento.status = new_status
            orcamento.atualizado_em = datetime.now()
            db.commit()
            return OrcamentoResponse.model_validate(orcamento)

    def update(self, orcamento):
        with get_db_session() as db:
            orcamento_repo = OrcamentoRepository(db)
            return orcamento_repo.update(orcamento)

    def delete(self, orcamento):
        with get_db_session() as db:
            orcamento_repo = OrcamentoRepository(db)
            return orcamento_repo.delete(orcamento)