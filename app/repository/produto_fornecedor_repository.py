from sqlalchemy.orm import Session, joinedload
from app.models.produto_fornecedor import ProdutoFornecedor

class ProdutoFornecedorRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, produto_fornecedor: ProdutoFornecedor):
        self.db.add(produto_fornecedor)
        self.db.flush()
        self.db.refresh(produto_fornecedor)
        return produto_fornecedor

    def get_by_id(self, id_produto_fornecedor):
        return (
            self.db.query(ProdutoFornecedor)
            .options(joinedload(ProdutoFornecedor.fornecedor))
            .filter(ProdutoFornecedor.id_produto_fornecedor == id_produto_fornecedor)
            .first()
        )

    def get_by_produto(self, id_produto):
        return (
            self.db.query(ProdutoFornecedor)
            .options(joinedload(ProdutoFornecedor.fornecedor))
            .filter(ProdutoFornecedor.id_produto == id_produto)
            .all()
        )