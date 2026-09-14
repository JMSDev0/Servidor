from sqlalchemy.orm import Session, joinedload
from app.models.pedido import Pedido
from app.models.item_pedido import ItemPedido
from app.models.cliente import Cliente
from uuid import UUID
from sqlalchemy import func
from app.enums.pedido_enums import StatusPedido
class PedidoRepository():
    def __init__(self, db: Session):
        self.db = db

    def save(self, pedido: Pedido) -> Pedido:
        self.db.add(pedido)
        self.db.flush()
        self.db.refresh(pedido)
        return pedido

    # joinedload de itens: sem isso, `pedido.itens` só carrega dentro da
    # sessão que buscou o objeto — quem chama fora do `with get_db_session()`
    # (ex: serialização da resposta) recebe uma coleção vazia/lazy nunca
    # disparada, e o frontend quebra em `pedido.itens.map(...)`.
    def get_by_id(self, id_pedido: UUID) -> Pedido:
        return (
            self.db.query(Pedido)
            .options(joinedload(Pedido.itens), joinedload(Pedido.cliente))
            .filter(Pedido.id_pedido == id_pedido)
            .first()
        )

    def get_by_cliente(self, id_cliente: UUID) -> list[Pedido]:
        return (
            self.db.query(Pedido)
            .options(joinedload(Pedido.itens), joinedload(Pedido.cliente))
            .filter(Pedido.id_cliente == id_cliente)
            .all()
        )

    def find_paginated(
        self,
        page: int,
        size: int,
        status: StatusPedido | None = None,
        id_cliente: UUID | None = None,
        cliente: str | None = None,
    ) -> list[Pedido]:
        offset = page * size
        query = self.db.query(Pedido).options(joinedload(Pedido.itens), joinedload(Pedido.cliente))
        if status is not None:
            query = query.filter(Pedido.status == status)
        if id_cliente is not None:
            query = query.filter(Pedido.id_cliente == id_cliente)
        if cliente:
            query = query.join(Pedido.cliente).filter(Cliente.nome.ilike(f"%{cliente}%"))
        return (
            query.order_by(Pedido.data_pedido.desc())
            .offset(offset)
            .limit(size)
            .all()
        )

    def count(
        self,
        status: StatusPedido | None = None,
        id_cliente: UUID | None = None,
        cliente: str | None = None,
    ) -> int:
        query = self.db.query(Pedido)
        if status is not None:
            query = query.filter(Pedido.status == status)
        if id_cliente is not None:
            query = query.filter(Pedido.id_cliente == id_cliente)
        if cliente:
            query = query.join(Pedido.cliente).filter(Cliente.nome.ilike(f"%{cliente}%"))
        return query.count()

    def delete(self, pedido: Pedido):
        self.db.delete(pedido)
        self.db.flush()

    def save_item(self, item_data: ItemPedido):
        self.db.add(item_data)
        self.db.flush()
        self.db.refresh(item_data)
        return item_data

    def get_total_mouth_sales(self):
        from datetime import datetime, timedelta
        today = datetime.now()
        first_day_of_month = today.replace(day=1)
        total_sales = self.db.query(func.sum(Pedido.valor_total)).filter(
            Pedido.data_pedido >= first_day_of_month,
            Pedido.status != StatusPedido.CANCELADO,
            Pedido.status != StatusPedido.PENDENTE
        ).scalar()
        return total_sales if total_sales is not None else 0
    