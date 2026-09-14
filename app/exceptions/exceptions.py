class EntityNotFoundException(Exception):
    def __init__(self, entity_id):
        self.entity_id = entity_id
        super().__init__(f"Entidade com ID {entity_id} não encontrada.")

class UnauthorizedException(Exception):
    def __init__(self, message: str = "Acesso não autorizado."):
        self.message = message
        super().__init__(self.message)

class DataBaseException(Exception):
    def __init__(self, message: str = "Erro no banco de dados."):
        self.message = message
        super().__init__(self.message)

class ClienteJaCadastradoException(Exception):
    def __init__(self, message: str = "Já existe uma conta com esse cpf/cnpj ou email."):
        self.message = message
        super().__init__(self.message)

class RequiredFieldNotFound(Exception):
    def __init__(self, field):
        super().__init__(f'Campo requerido "{field}" não encontrado')