import os
import datetime
from collections.abc import AsyncGenerator

from sqlalchemy import Enum, String, UniqueConstraint, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TIMESTAMP

from app.models.application import ApplicationStatus

DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
test_engine = create_async_engine(TEST_DATABASE_URL)


#Session object maker
async_session_local = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

async_test_session_local = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_local() as session:
        yield session

#Table creation layout
class Base(DeclarativeBase):
    pass

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint(
            "company",
            "position",
            name="uq_application_company_position"
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        unique=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        deferred=True, 
        nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable = False, 
        server_default=text('now()')
    )
