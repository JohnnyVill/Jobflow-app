import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from fastapi import status, HTTPException, Depends
from typing import Annotated
from app.models.token_response import TokenData
from app.core.security import key, token_algorithm
from app.db.database import User
from app.models.users import UserCreation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import undefer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def register_user(user: UserCreation, db: AsyncSession):
    try:
        async with db.begin():
            new_user = User(email = user.email)
            new_user.password = user.password

            db.add(new_user)
            return new_user
    except IntegrityError:
        return None

async def get_user(user_id: int, db: AsyncSession):
    statement = select(User).where(User.id == user_id)
    current_user = await db.execute(statement)
    return current_user.scalar_one_or_none()


async def authenticate_user(credentials: UserCreation,db:AsyncSession):
    #Selecting the User table and checking if the credential pass match and email the table
    result = await db.execute(
        select(User)
        .options(undefer(User.password_hash))
        .where(User.email == credentials.email)
    )

    user = result.scalar_one_or_none()
    #check if user is valid and if the password is valid for that user
    if user is None:
        #still check user here to prevent timing attacks
        return None
    if not user.check_password(credentials.password):
        return None

    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db:AsyncSession):
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
    user = await get_user(user_id=int(token_data.user_id),db=db)
    if user is None:
        raise credentials_exception
    return user