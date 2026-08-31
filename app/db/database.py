import os
from collections.abc import AsyncGenerator

from sqlalchemy import Enum, String, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

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

test_async_session_local = async_sessionmaker(
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
