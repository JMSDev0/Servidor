from fastapi import APIRouter, Depends, HTTPException
from app.service.auth_service import authenticate
from app.schemas.login_schema import LoginSchema

auth = APIRouter()

@auth.post("/login")
async def login(login_data: LoginSchema):
    token = authenticate(login_data.login, login_data.password, type=login_data.type if login_data.type else "cliente")
    if not token:
        raise HTTPException(status_code=401, detail="Invalid login or password")
    return {"token": token[0], "payload": token[1]}
