from app.repository.pedido_repository import PedidoRepository
from app.service.produto_service import ProdutoService
from app.models.pedido import Pedido
from app.schemas.pedido.pedido_create import PedidoCreate, PedidoItemCreate
from app.service.auth_service import check_user_permission
from app.db.config import get_db_session
from app.service.cliente_service import ClienteService
from app.service.produto_service import ProdutoService
from app.schemas.movimentacao_estoque import MovimentacaoEstoqueCreate
from app.enums.tipo_movimentacao import TipoMovimentacao
from app.models.item_pedido import ItemPedido
from app.enums.pedido_enums import StatusPedido
from app.models.orcamento import Orcamento
from app.enums.tipo_producao import TipoProducao
from app.schemas.pedido.pedido_response import PedidoResponse
from app.schemas.page_model import PageModel
from uuid import UUID

from app.exceptions.exceptions import RequiredFieldNotFound


class PedidoService:
    def __init__(self):
        pass
    
    def save(self, pedido: PedidoCreate, current_user: dict, internal: bool = False):
        client = None
        func = None

        if internal:
            func = check_user_permission(current_user, repo="funcionario")
        else:
            client = check_user_permission(current_user, repo="cliente")

        if client is not None:
            pedido.id_cliente = client.id_cliente

        self._validate_create(pedido)

        with get_db_session() as db:
            pedido_repository = PedidoRepository(db)
            pedido_data = pedido.model_dump()

            if func is not None:
                pedido_data["id_funcionario"] = func.id_funcionario

            client_service = ClienteService()

            if pedido.id_endereco_entrega is not None:
                endereco = client_service.get_endereco_by_id(pedido.id_endereco_entrega)

                if endereco is None:
                    raise ValueError(
                        f"Endereço com ID {pedido.id_endereco_entrega} não encontrado."
                    )

                pedido_data["endereco_entrega_texto"] = (
                    f"{endereco.logradouro}, "
                    f"{endereco.numero}, "
                    f"{endereco.bairro}, "
                    f"{endereco.cidade} - "
                    f"{endereco.estado}, "
                    f"CEP: {endereco.cep}"
                )

            else:

                if pedido.endereco_entrega_texto is None:
                    raise ValueError(
                        "O pedido deve ter um endereço de entrega ou um endereço de entrega em texto."
                    )
                
                pedido_data["endereco_entrega_texto"] = pedido.endereco_entrega_texto

        

            pedido_model = Pedido(
                forma_pagamento=pedido.forma_pagamento,
                id_cliente=pedido.id_cliente,
                id_empresa_contrato=pedido.id_empresa_contrato,
                endereco_entrega_texto=pedido_data["endereco_entrega_texto"],
                id_funcionario=pedido_data.get("id_funcionario"),
                id_endereco_entrega=pedido.id_endereco_entrega,
                valor_total=0.0  # Inicializa o valor total do pedido como 0.0
            )

            pedido_salvo = pedido_repository.save(pedido_model)
            db.commit()

            valor_total_pedido = 0

            for item in pedido.itens:
                item_data = item.model_dump()
                item_data['id_pedido'] = pedido_model.id_pedido
                produto_service = ProdutoService()
                produto = produto_service.get_by_id(item.id_produto)
                if produto is None:
                    raise ValueError(f"Produto com ID {item.id_produto} não encontrado.")
                if produto.tipo_producao == TipoProducao.SOB_MEDIDA:
                    raise ValueError(
                        f"Produto '{produto.nome}' é sob medida — crie um orçamento em vez de um pedido direto."
                    )
                if produto.quantidade_estoque < item.quantidade:
                    raise ValueError(f"Estoque insuficiente para o produto {produto.nome}.")
                item_data['preco_unitario'] = produto.preco
                item_data['subtotal'] = produto.preco * item.quantidade

                pedido_repository.save_item(ItemPedido(**item_data))

                mov_data = MovimentacaoEstoqueCreate(
                    id_produto=item.id_produto,
                    quantidade=item.quantidade,
                    tipo_movimentacao=TipoMovimentacao.SAIDA,
                    id_pedido=pedido_model.id_pedido
                )
            
                produto_service.register_stock_movement(mov_data)

                valor_total_pedido += item_data['subtotal']

            pedido_salvo.valor_total = valor_total_pedido
            db.commit()
            db.refresh(pedido_salvo)
            return PedidoResponse.model_validate(pedido_salvo)


    def get_by_id(self, id_pedido: UUID, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            pedido_repository = PedidoRepository(db)
            pedido = pedido_repository.get_by_id(id_pedido)
            if not pedido:
                raise ValueError("Pedido não encontrado")
            return PedidoResponse.model_validate(pedido)

    def find(
        self,
        page: int,
        size: int,
        status: StatusPedido | None,
        current_user: dict,
        id_cliente: UUID | None = None,
        cliente: str | None = None,
    ):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            pedido_repository = PedidoRepository(db)
            pedidos = pedido_repository.find_paginated(page, size, status, id_cliente, cliente)
            total = pedido_repository.count(status, id_cliente, cliente)
            return PageModel(
                content=[PedidoResponse.model_validate(pedido) for pedido in pedidos],
                page=page,
                size=size,
                total_pages=(total + size - 1) // size if size else 0,
                total_items=total,
            )

    def get_by_cliente(self, id_cliente: UUID | None = None, current_user: dict = None, internal: bool = False):
        if not internal:
            cliente = check_user_permission(current_user, repo="cliente")
            id_cliente = cliente.id_cliente
        else:
            check_user_permission(current_user, repo="funcionario")
            if id_cliente is None:
                raise RequiredFieldNotFound(field="id_cliente")
        with get_db_session() as db:
            pedido_repository = PedidoRepository(db)
            pedidos = pedido_repository.get_by_cliente(id_cliente)
            return [PedidoResponse.model_validate(pedido) for pedido in pedidos]


    def update_status(self, id_pedido: UUID, status: StatusPedido, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            pedido_repository = PedidoRepository(db)
            pedido = pedido_repository.get_by_id(id_pedido)
            if not pedido:
                raise ValueError("Pedido não encontrado")
            self._validate_update_status(pedido.status, status)
            if status == StatusPedido.CANCELADO:
                produto_service = ProdutoService()
                for item in pedido.itens:
                    mov_data = MovimentacaoEstoqueCreate(
                        id_produto=item.id_produto,
                        quantidade=item.quantidade,
                        tipo_movimentacao=TipoMovimentacao.ENTRADA,
                        id_pedido=pedido.id_pedido
                    )
                    produto_service.register_stock_movement(mov_data)
            pedido.status = status
            db.commit()
            db.refresh(pedido)
            return PedidoResponse.model_validate(pedido)

    def save_from_orcamento(self, orcamento: Orcamento, forma_pagamento, id_endereco_entrega=None, endereco_entrega_texto=None):
        """
        O Orcamento não guarda forma de pagamento nem endereço de entrega —
        isso só é decidido no momento da aprovação (quando o orçamento vira
        pedido de fato), então esses dados vêm de fora, passados por quem
        aprovou (ver OrcamentoService.change_status). Mesma lógica de
        resolução de endereço usada em PedidoService.save().
        """
        if id_endereco_entrega is not None:
            client_service = ClienteService()
            endereco = client_service.get_endereco_by_id(id_endereco_entrega)
            if endereco is None:
                raise ValueError(f"Endereço com ID {id_endereco_entrega} não encontrado.")
            endereco_entrega_texto = (
                f"{endereco.logradouro}, "
                f"{endereco.numero}, "
                f"{endereco.bairro}, "
                f"{endereco.cidade} - "
                f"{endereco.estado}, "
                f"CEP: {endereco.cep}"
            )

        if endereco_entrega_texto is None:
            raise ValueError(
                "É necessário informar um endereço de entrega (id_endereco_entrega ou endereco_entrega_texto) para aprovar o orçamento."
            )

        with get_db_session() as db:
            pedido_repository = PedidoRepository(db)
            pedido_data = Pedido(
                forma_pagamento=forma_pagamento,
                id_cliente=orcamento.id_cliente,
                id_empresa_contrato=orcamento.id_empresa_contrato,
                id_orcamento=orcamento.id_orcamento,
                endereco_entrega_texto=endereco_entrega_texto,
                id_funcionario=orcamento.id_funcionario,
                id_endereco_entrega=id_endereco_entrega,
                valor_total=orcamento.valor_total
            )
            pedido_salvo = pedido_repository.save(pedido_data)
            db.commit()

            for item in orcamento.itens:
                item_data = ItemPedido(
                    id_pedido=pedido_salvo.id_pedido,
                    id_produto=item.id_produto,
                    quantidade=item.quantidade,
                    preco_unitario=item.preco_unitario,
                    subtotal=item.subtotal
                )
                pedido_repository.save_item(item_data)

            db.commit()
            db.refresh(pedido_salvo)
            return pedido_salvo

    def _validate_create(self, pedido: PedidoCreate):
        if not pedido.itens or len(pedido.itens) == 0:
            raise ValueError("O pedido deve conter pelo menos um item.")

        if pedido.id_cliente is None and pedido.id_empresa_contrato is None:
            raise ValueError("O pedido deve ter um cliente ou uma empresa de contrato associada.")


    def _validate_update_status(self, old_status: StatusPedido, new_status: StatusPedido):
        valid_transitions = {
            StatusPedido.PENDENTE: [StatusPedido.PAGO, StatusPedido.CANCELADO],
            StatusPedido.PAGO: [StatusPedido.EM_SEPARACAO, StatusPedido.CANCELADO],
            StatusPedido.EM_SEPARACAO: [StatusPedido.ENVIADO, StatusPedido.CANCELADO],
            StatusPedido.ENVIADO: [StatusPedido.ENTREGUE, StatusPedido.CANCELADO],
            StatusPedido.ENTREGUE: [],
            StatusPedido.CANCELADO: []
        }
        if new_status not in valid_transitions[old_status]:
            raise ValueError(f"Transição de status inválida: {old_status} → {new_status}")

    def get_mouth_sales(self, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            pedido_repository = PedidoRepository(db)
            return pedido_repository.get_total_mouth_sales()
        