from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import undefer

from app.db.database import Application, User
from app.models.application import JobApplication
from app.models.users import UserCreation, UserResponse
from app.models.token_response import TokenData
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from app.core.security import key,token_algorithm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_user(user: UserResponse, db: AsyncSession):
    statement = select(User).where(User.id == user.id)
    current_user = await db.execute(statement)
    return current_user.scalar_one_or_none()


async def create_application(application: JobApplication, db: AsyncSession):
    #check if application already exist
    try:
        async with db.begin():
            new_application = Application(
                company=application.company,
                position=application.position,
                status=application.status
            )
            db.add(new_application)
            return new_application
    except IntegrityError:
        return None


async def register_user(user: UserCreation, db: AsyncSession):
    try:
        async with db.begin():
            new_user = User(email = user.email)
            new_user.password = user.password

            db.add(new_user)
            return new_user
    except IntegrityError:
        return None


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

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
    user = get_user(user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_applications(db: AsyncSession):
    applications = await db.execute(select(Application))
    return applications.scalars().all()

    
async def get_application(application_id: int, db: AsyncSession):
    statement = select(Application).where(Application.id == application_id)
    application = await db.execute(statement)
    return application.scalar_one_or_none()


async def delete_application(application_id: int, db: AsyncSession):
    result = await db.execute(
        delete(Application)
        .where(Application.id == application_id)
        .returning(Application.id, Application.company, Application.position)
    )
    deleted_application = result.first()
    await db.commit()
    return deleted_application