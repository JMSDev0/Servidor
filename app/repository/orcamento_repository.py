from app.models.orcamento import Orcamento
from app.models.item_orcamento import ItemOrcamento
from app.models.cliente import Cliente
from sqlalchemy.orm import Session, joinedload

class OrcamentoRepository:
    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        return self.db.query(Orcamento).options(
            joinedload(Orcamento.itens).joinedload(ItemOrcamento.produto),
            joinedload(Orcamento.cliente),
        )

    def get_orcamento_by_id(self, id_orcamento):
        return self._base_query().filter(Orcamento.id_orcamento == id_orcamento).first()

    def list_by_status(self, status):
        return self._base_query().filter(Orcamento.status == status).all()

    def find_paginated(self, page: int, size: int, status=None, id_cliente=None, cliente=None):
        offset = page * size
        query = self._base_query()
        if status is not None:
            query = query.filter(Orcamento.status == status)
        if id_cliente is not None:
            query = query.filter(Orcamento.id_cliente == id_cliente)
        if cliente:
            query = query.join(Orcamento.cliente).filter(Cliente.nome.ilike(f"%{cliente}%"))
        return (
            query.order_by(Orcamento.criado_em.desc())
            .offset(offset)
            .limit(size)
            .all()
        )

    def count(self, status=None, id_cliente=None, cliente=None) -> int:
        query = self.db.query(Orcamento)
        if status is not None:
            query = query.filter(Orcamento.status == status)
        if id_cliente is not None:
            query = query.filter(Orcamento.id_cliente == id_cliente)
        if cliente:
            query = query.join(Orcamento.cliente).filter(Cliente.nome.ilike(f"%{cliente}%"))
        return query.count()

    def save(self, orcamento: Orcamento):
        self.db.add(orcamento)
        self.db.flush()
        self.db.refresh(orcamento)
        return orcamento

    def update(self, orcamento: Orcamento):
        self.db.merge(orcamento)
        self.db.flush()
        self.db.refresh(orcamento)
        return orcamento

    def delete(self, orcamento: Orcamento):
        self.db.delete(orcamento)
        self.db.flush()


    def save_item_orcamento(self, item_orcamento: ItemOrcamento):
        self.db.add(item_orcamento)
        self.db.flush()
        self.db.refresh(item_orcamento)
        return item_orcamento


    def get_item_orcamento_by_id(self, id_item_orcamento):
            return self.db.query(ItemOrcamento).filter(ItemOrcamento.id_item_orcamento == id_item_orcamento).first()

