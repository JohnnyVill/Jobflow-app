from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import undefer

from app.db.database import User, get_db
from app.models.users import UserCreation

DbSession = Annotated[AsyncSession, Depends(get_db)]

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

