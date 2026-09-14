from abc import ABC, abstractmethod


class Storage(ABC):
    """
    Interface abstrata para serviços de armazenamento de arquivos.

    Define as operações necessárias para:
    - gerar uma URL temporária para upload de um arquivo;
    - gerar uma URL temporária para leitura de um arquivo.

    A implementação concreta é responsável por definir como essas
    operações serão realizadas no serviço de armazenamento utilizado.
    """

    @abstractmethod
    def create_upload_url(self, filename):
        """
        Gera uma URL temporária para realizar o upload de um arquivo.

        Args:
            filename: Nome do arquivo que será enviado.

        Returns:
            Um dicionário contendo a URL temporária de upload e a
            identificação do objeto armazenado.

        Raises:
            ValueError: Caso o arquivo não possua um formato permitido.
        """
        pass

    @abstractmethod
    def create_read_url(self, object_key):
        """
        Gera uma URL temporária para acessar um arquivo armazenado.

        Args:
            object_key: Identificador do objeto dentro do armazenamento.

        Returns:
            URL temporária que permite acessar o arquivo.

        Raises:
            ValueError: Caso o identificador do objeto seja inválido.
        """
        pass