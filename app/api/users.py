from typing import Annotated
from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException
from app.models.users import UserCreation, UserResponse
from app.services.auth_service import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

users_router = APIRouter(
    prefix="/users", 
    tags=["users"]
)
DbSession = Annotated[AsyncSession, Depends(get_db)]

@users_router.get("/me", response_model=UserResponse)
def get_user(db:DbSession):
    pass