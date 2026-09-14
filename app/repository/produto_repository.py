from app.models.produto import Produto
from app.models.categoria import Categoria
from app.models.movimentacao_estoque import MovimentacaoEstoque
from sqlalchemy.orm import Session
from app.models.produto_fornecedor import ProdutoFornecedor
from sqlalchemy import func

class ProdutoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id):
        return self.db.query(Produto).filter(Produto.id_produto == id).first()

    def save(self, produto: Produto):
        self.db.add(produto)
        self.db.flush()
        self.db.refresh(produto)
        return produto

    def get_all(self):
        return self.db.query(Produto).filter(Produto.ativo == True).all()

    def delete(self, produto: Produto):
        self.db.delete(produto)

    def soft_delete(self, produto: Produto):
        produto.ativo = False
        self.db.add(produto)
        self.db.flush()
        self.db.refresh(produto)
        return produto

    def find_paginated(self, page: int, size: int):
        offset = page * size
        # outerjoin (não join): id_categoria é anulável (ondelete="SET NULL"),
        # um INNER JOIN escondia da listagem qualquer produto ativo sem categoria.
        return self.db.query(Produto).filter(Produto.ativo == True).outerjoin(Categoria).offset(offset).limit(size).all()

    def count(self):
        return self.db.query(Produto).count()

    def _filtered_query_internal(self, nome=None, id_categoria=None, tipo_producao=None, ativo=None):
        # Tela de gestão (staff): ao contrário de find_paginated (catálogo
        # público, sempre só ativos), aqui ativo=None mostra os dois estados —
        # quem gerencia precisa enxergar produtos desativados pra reativar/auditar.
        query = self.db.query(Produto).outerjoin(Categoria)
        if nome:
            query = query.filter(Produto.nome.ilike(f"%{nome}%"))
        if id_categoria is not None:
            query = query.filter(Produto.id_categoria == id_categoria)
        if tipo_producao is not None:
            query = query.filter(Produto.tipo_producao == tipo_producao)
        if ativo is not None:
            query = query.filter(Produto.ativo == ativo)
        return query

    def find_paginated_internal(self, page: int, size: int, nome=None, id_categoria=None, tipo_producao=None, ativo=None):
        offset = page * size
        return (
            self._filtered_query_internal(nome, id_categoria, tipo_producao, ativo)
            .order_by(Produto.nome)
            .offset(offset)
            .limit(size)
            .all()
        )

    def count_internal(self, nome=None, id_categoria=None, tipo_producao=None, ativo=None) -> int:
        return self._filtered_query_internal(nome, id_categoria, tipo_producao, ativo).count()

    def register_stock_movement(self, movimentacao: MovimentacaoEstoque):
        self.db.add(movimentacao)
        self.db.flush()
        self.db.refresh(movimentacao)
        return movimentacao

    def get_by_fornecedor(self, id_fornecedor):
        return self.db.query(Produto).join(ProdutoFornecedor).filter(ProdutoFornecedor.id_fornecedor == id_fornecedor).all()

    def get_movimentacoes_by_produto(self, id_produto):
        return self.db.query(MovimentacaoEstoque).filter(MovimentacaoEstoque.id_produto == id_produto).all()

    def get_quantity_produtos_in_stock(self):
        return self.db.query(func.sum(Produto.quantidade_estoque)).filter(Produto.ativo == True).scalar()        
    