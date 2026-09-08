from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.users import UserCreation, UserResponse
from app.services.application_service import authenticate_user, register_user
from app.core.security import create_access_token
from app.models.token_response import TokenResponse

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

@auth_router.post("/login", response_model=TokenResponse)
async def login(user: UserCreation, db: DbSession):
    authenticated_user = await authenticate_user(user, db)
    if  authenticated_user:
        token = create_access_token(authenticated_user)
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    raise HTTPException(status_code=401, detail="Invalid email or password")