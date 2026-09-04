# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.db.database import get_db
# from app.models.application import UserCreation,UserResponse

# from app.services.application_service import (
#     create_user,
#     get_users
# )

# users_router = APIRouter(
#     prefix="/users", 
#     tags=["users"]
# )

# @users_router.post("", response_model=UserResponse)
# async def make_user(user: UserCreation, db: AsyncSession = Depends(get_db)):
#     success = await create_user(user, db)
#     if success:
#         return success
#     raise HTTPException(status_code=409, detail="Email already in use")

# @users_router.get("", response_model=list[UserResponse])
# async def get_all_users(db: AsyncSession = Depends(get_db)):
#     users = await get_users(db)
#     if  users:
#         return users
#     raise HTTPException(status_code=404, detail="Users not found")