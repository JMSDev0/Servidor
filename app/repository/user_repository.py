from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def get_by_login(self, login: str):
        pass

    @abstractmethod
    def get_by_id(self, id: str):
        pass

    @abstractmethod
    def get_by_email(self, email: str):
        pass
