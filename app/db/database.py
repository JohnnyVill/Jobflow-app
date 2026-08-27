import asyncio
import os

from sqlalchemy import String, select, Enum
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker
    )
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import OperationalError
from app.models.application import ApplicationStatus

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)


#Session object maker
async_session_local = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


#Table creation layout
class Base(DeclarativeBase):
    pass

class Application(Base):
    __tablename__ = "application"

    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), nullable=False)
