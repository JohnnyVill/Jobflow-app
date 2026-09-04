from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.application import UserCreation,UserResponse

from app.services.application_service import (
    create_user,
    get_user
)

auth_router = APIRouter(
    prefix="/auth", 
    tags=["auth"]
)

@auth_router.post("/register", response_model=UserResponse)
async def register(user: UserCreation, db: AsyncSession = Depends(get_db)):
    success = await create_user(user, db)
    if success:
        return success
    raise HTTPException(status_code=409, detail="Email already in use")

@auth_router.get("/login", response_model=list[UserResponse])
async def login(user: UserCreation, db: AsyncSession = Depends(get_db)):
    users = await get_user(user, db)
    if  users:
        return users
    raise HTTPException(status_code=404, detail="Users not found")