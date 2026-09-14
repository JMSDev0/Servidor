from app.repository.user_repository import UserRepository
from app.models.cliente import Cliente
from app.models.endereco_cliente import EnderecoCliente
from sqlalchemy.orm import Session
from sqlalchemy import or_
from uuid import UUID

class ClienteRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_login(self, login: str) -> Cliente:
        return self.db.query(Cliente).filter(Cliente.login == login).first()

    def get_by_documento_or_email(self, cpf_cnpj: str, email: str) -> Cliente:
        return self.db.query(Cliente).filter(
            or_(Cliente.cpf_cnpj == cpf_cnpj, Cliente.email == email)
        ).first()

    def get_by_documento_and_email(self, cpf_cnpj: str, email: str) -> Cliente:
        return self.db.query(Cliente).filter(
            Cliente.cpf_cnpj == cpf_cnpj, Cliente.email == email
        ).first()

    def save(self, cliente: Cliente) -> Cliente:
        self.db.add(cliente)
        self.db.flush()
        self.db.refresh(cliente)
        return cliente

    def get_by_id(self, id: UUID) -> Cliente:
        return self.db.query(Cliente).filter(Cliente.id_cliente == id).first()

    def get_by_email(self, email: str) -> Cliente:
        return self.db.query(Cliente).filter(Cliente.email == email).first()
    
    def get_all(self) -> list[Cliente]:
        return self.db.query(Cliente).all()

    def find_paginated(self, page: int, size: int) -> list[Cliente]:
        offset = page * size
        return self.db.query(Cliente).offset(offset).limit(size).all()

    def count(self) -> int:
        return self.db.query(Cliente).count()

    def get_endereco_by_id(self, id: UUID) -> EnderecoCliente:
        return self.db.query(EnderecoCliente).filter(EnderecoCliente.id_endereco == id).first()

    def save_endereco(self, endereco: EnderecoCliente) -> EnderecoCliente:
        self.db.add(endereco)
        self.db.flush()
        self.db.refresh(endereco)
        return endereco

    def get_enderecos_by_cliente_id(self, id_cliente: UUID) -> list[EnderecoCliente]:
        return self.db.query(EnderecoCliente).filter(EnderecoCliente.id_cliente == id_cliente).all()

    def marcar_endereco_principal(self, endereco: EnderecoCliente):
        # Desmarca todos os endereços do cliente como não principal
        self.db.query(EnderecoCliente).filter(
            EnderecoCliente.id_cliente == endereco.id_cliente
        ).update({EnderecoCliente.principal: False})
        # Marca o endereço fornecido como principal
        endereco.principal = True
        self.db.add(endereco)
        self.db.flush()
        self.db.refresh(endereco)