from fastapi import APIRouter, Depends
from app.models.users import UserResponse
from app.services.auth_service import get_current_user
from app.db.database import User

users_router = APIRouter(
    prefix="/users", 
    tags=["users"]
)


@users_router.get("/me", response_model=UserResponse)
def get_user(current_user: User = Depends(get_current_user)):
    return current_user