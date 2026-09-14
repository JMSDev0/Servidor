from fastapi import APIRouter, Depends, HTTPException
from app.service.auth_service import verify_token
from app.storage.storage_factory import StorageFactory

upload_router = APIRouter(prefix="/internal")

storage = StorageFactory.get_storage()

@upload_router.post("/url")
def create_upload_url(filename: str):
    try:
        result = storage.create_upload_url(filename)

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
    
@upload_router.get("/url")
def create_read_url(object_key: str):
    try:
        image_url = storage.create_read_url(object_key)

        return {
            "image_url": image_url
        }

    except Exception as error:
        print(f"Erro ao gerar URL de leitura: {error}")

        raise HTTPException(
            status_code=500,
            detail="Não foi possível gerar a URL da imagem"
        )