from app.models.funcionario import Funcionario
from sqlalchemy.orm import Session
from uuid import UUID
from app.repository.user_repository import UserRepository

class FuncionarioRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_funcionarios(self, page: int, size: int, filters: dict):
        query = self.db.query(Funcionario)
        offset = page * size

        # Apply filters
        if 'nome' in filters:
            query = query.filter(Funcionario.nome.ilike(f"%{filters['nome']}%"))
        if 'cpf' in filters:
            query = query.filter(Funcionario.cpf == filters['cpf'])
        if 'email' in filters:
            query = query.filter(Funcionario.email == filters['email'])
        if 'login' in filters:
            query = query.filter(Funcionario.login == filters['login'])
        if 'tipo' in filters:
            if isinstance(filters['tipo'], list):
                query = query.filter(Funcionario.tipo.in_(filters['tipo']))
            else:
                query = query.filter(Funcionario.tipo == filters['tipo'])
        if 'ativo' in filters:
            query = query.filter(Funcionario.ativo == filters['ativo'])

        total_count = query.count()
        funcionarios = query.offset(offset).limit(size).all()

        return funcionarios, total_count
    def get_by_login(self, login: str) -> Funcionario:
        return self.db.query(Funcionario).filter(Funcionario.login == login).first()

    def get_by_cpf(self, cpf: str) -> Funcionario:
        return self.db.query(Funcionario).filter(Funcionario.cpf == cpf).first()

    def get_by_email(self, email: str) -> Funcionario:
        return self.db.query(Funcionario).filter(Funcionario.email == email).first()

    def save(self, funcionario: Funcionario) -> Funcionario:
        self.db.add(funcionario)
        self.db.flush()
        self.db.refresh(funcionario)
        return funcionario

    def get_by_id(self, id: UUID) -> Funcionario:
        return self.db.query(Funcionario).filter(Funcionario.id_funcionario == id).first()

    def get_by_email(self, email: str) -> Funcionario:
        return self.db.query(Funcionario).filter(Funcionario.email == email).first()
