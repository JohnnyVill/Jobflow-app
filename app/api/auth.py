from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.users import UserCreation, UserResponse
from app.services.application_service import authenticate_user, register_user
from app.core.security import create_access_token

auth_router = APIRouter(
    prefix="/auth", 
    tags=["auth"]
)

DbSession = Annotated[AsyncSession, Depends(get_db)]

@auth_router.post("/register", response_model=UserResponse)
async def register(user: UserCreation, db: DbSession):
    success = await register_user(user, db)
    if success:
        return success
    raise HTTPException(status_code=409, detail="Email already in use")

@auth_router.post("/login", response_model=UserResponse)
async def login(user: UserCreation, db: DbSession):
    authenticated_user = await authenticate_user(user, db)
    if  authenticated_user:
        create_access_token(authenticated_user)
        return authenticated_user
    raise HTTPException(status_code=401, detail="Invalid email or password")