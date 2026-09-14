from app.models.empresa_contrato import EmpresaContrato
from sqlalchemy.orm import Session 

class EmpresaContratoRepository:
    def __init__(self, db: Session = None):
        self.db = db

    def save(self, emp: EmpresaContrato):
        self.db.add(emp)
        self.db.flush()
        self.db.refresh(emp)
        return emp

    def get_by_id(self, id):
        return self.db.query(EmpresaContrato).filter(EmpresaContrato.id_empresa_contrato == id).first()

    def get_by_cnpj(self, cnpj: str):
        return self.db.query(EmpresaContrato).filter(EmpresaContrato.cnpj == cnpj).first()

    def get_all(self):
        return self.db.query(EmpresaContrato).all()

    def find_paginated(self, page: int, size: int):
        return self.db.query(EmpresaContrato).offset(page * size).limit(size).all()

    def delete(self, emp: EmpresaContrato):
        self.db.delete(emp)
        self.db.flush()

    def count(self):
        return self.db.query(EmpresaContrato).count()
    