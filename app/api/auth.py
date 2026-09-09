from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from app.models.token_response import TokenData

from app.db.database import get_db
from app.models.users import UserCreation, UserResponse
from app.services.application_service import authenticate_user, register_user
from app.core.security import create_access_token
from app.models.token_response import TokenResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.security import key,token_algorithm
from jwt.exceptions import InvalidTokenError
from app.services.application_service import get_user

auth_router = APIRouter(
    prefix="/auth", 
    tags=["auth"]
)

DbSession = Annotated[AsyncSession, Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

@auth_router.get("/me")
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db:AsyncSession= Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key, algorithms=[token_algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id = user_id)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(user_id=token_data.user_id,db=db)
    if user is None:
        raise credentials_exception
    return user