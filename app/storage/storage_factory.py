from app.storage.oracle_storage import OracleStorage
from app.storage.local_storage import LocalStorage
from app.storage.storage import Storage
from dotenv import load_dotenv
import os

load_dotenv()

class StorageFactory:

    CLASSES = {
        "oracle": OracleStorage,
        "local": LocalStorage
    }

    @classmethod
    def get_storage(cls) -> Storage:
        storage_type = os.getenv("STORAGE_TYPE", "local")
        storage_class = cls.CLASSES.get(storage_type)

        if not storage_class:
            raise ValueError(f"Storage type '{storage_type}' is not supported.")

        return storage_class()