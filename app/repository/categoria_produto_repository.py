from app.models.categoria import Categoria
from sqlalchemy.orm import Session

class CategoriaProdutoRepository():
    def __init__(self, db):
        self.db = db

    def get_by_id(self, id):
        return self.db.query(Categoria).filter(Categoria.id_categoria == id).first()

    def get_by_nome(self, nome):
        return self.db.query(Categoria).filter(Categoria.nome == nome).first()

    def save(self, categoria: Categoria):
        self.db.add(categoria)
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def get_all(self):
        return self.db.query(Categoria).all()

    def find_paginated(self, page: int, size: int):
        offset = page * size
        return self.db.query(Categoria).offset(offset).limit(size).all()

    def delete(self, categoria: Categoria):
        self.db.delete(categoria)
        self.db.commit()

    def count(self):
        return self.db.query(Categoria).count()

    