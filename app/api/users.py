from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.db.database import User
from app.models.users import UserResponse

users_router = APIRouter(
    prefix="/users", 
    tags=["users"]
)

CurrentUser = Annotated[User, Depends(get_current_user)]

@users_router.get("/me", response_model=UserResponse)
def get_user(current_user:CurrentUser):
    return current_user