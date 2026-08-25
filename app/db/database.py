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


#Test engine connection
# async def test_connection():
#     try:
#         async with engine.connect() as connection:
#             result = await connection.execute(text("SElECT 1"))
#             print(result.scalar())
#         print("Connection Successfull")
#     except OperationalError as e:
#         print(f"Connection Failed: {e}")


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

class Applications(Base):
    __tablename__ = "application"

    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), nullable=False)

# async def create_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     print("Table created")


#verify if sessions are made
async def test_session():
    async with async_session_local() as session:
        async with session.begin():
            first_test = Applications(company = "Google", position = "Software Engineer", status = ApplicationStatus.OFFER)
            session.add(first_test)

        result = await session.execute(select(Applications))
        test_result = result.scalars().all()
        for t in test_result:
            print(t.company, t.position, t.status)


async def main():
    # await create_tables()
    await test_session()

if __name__ == "__main__":
    asyncio.run(main())