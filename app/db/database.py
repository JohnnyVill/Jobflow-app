import os
import datetime
import bcrypt
from collections.abc import AsyncGenerator

from sqlalchemy import Enum, String, UniqueConstraint, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.hybrid import hybrid_property
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

    @hybrid_property
    def password(self):
        """Getter prevents reading the plain text password"""
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, plaintext_password: str) -> None:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plaintext_password.encode('utf-8'), salt)
        self.password_hash = hashed.decode('utf-8')

    def check_password(self, plaintext_password: str) -> bool:
        return bcrypt.checkpw(
            plaintext_password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )    
        
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable = False, 
        server_default=text('now()')
    )
