from app.repository.funcionario_repository import FuncionarioRepository
from app.repository.user_repository import UserRepository
from app.repository.cliente_repository import ClienteRepository

class RepoFactory():

    repos: dict[str, type[UserRepository]] = {
        "funcionario": FuncionarioRepository,
        "cliente": ClienteRepository,
    }

    @classmethod
    def get_repository(cls, repo_name: str) -> type[UserRepository]:
        repo_class = cls.repos.get(repo_name)
        if not repo_class:
            raise ValueError(f"Repository '{repo_name}' not found.")
        return repo_class
