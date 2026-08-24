import asyncio

from sqlalchemy import text, String
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker
    )
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import OperationalError 

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/jobflow"
engine = create_async_engine(DATABASE_URL)

#Test engine connection
async def test_connection():
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SElECT 1"))
            print(result.scalar())
        print("Connection Successfull")
    except OperationalError as e:
        print(f"Connection Failed: {e}")

asyncio.run(test_connection())

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

class Test(Base):
    __tablename__ = "test"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    def __repr__(self) -> str:
        return f"Test(id={self.id!r},name={self.name!r})"

print(Base.metadata.tables)