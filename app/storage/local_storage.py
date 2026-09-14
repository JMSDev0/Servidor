from app.storage.storage import Storage

class LocalStorage(Storage):
    def create_upload_url(self, filename):
        return {
            "upload_url": f"http://localhost:8000/upload/{filename}",
            "object_key": filename
        }

    def create_read_url(self, object_key):
        # Implementação para criar uma URL de leitura local
        return f"http://localhost:8000/files/{object_key}"