from sqlalchemy.orm import Session
from app.models.fornecedor import Fornecedor

class FornecedorRepository():
    def __init__(self, db: Session):
        self.db = db

    def save(self, fornecedor: Fornecedor) -> Fornecedor:
        self.db.add(fornecedor)
        self.db.flush()
        self.db.refresh(fornecedor)
        return fornecedor

    def get_by_cnpj(self, cnpj: str) -> Fornecedor:
        return self.db.query(Fornecedor).filter(Fornecedor.cnpj == cnpj).first()

    def get_by_id(self, id: str) -> Fornecedor:
        return self.db.query(Fornecedor).filter(Fornecedor.id_fornecedor == id).first()

    def list_all(self) -> list[Fornecedor]:
        return self.db.query(Fornecedor).all()

    def find(self, page: int, size: int) -> list[Fornecedor]:
        offset = page * size
        return self.db.query(Fornecedor).offset(offset).limit(size).all()

    def count(self) -> int:
        return self.db.query(Fornecedor).count()
