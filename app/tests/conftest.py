import os
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_db

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
test_engine = create_async_engine(TEST_DATABASE_URL)

#Test Session object maker
async_test_session_local = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

#Override get_db to use the test session 
async def override_get_db():
    async with async_test_session_local() as session:
        yield session
app.dependency_overrides[get_db] = override_get_db


#use this local testing area to run test 
@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        yield client

#resets the table for every test
@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    async with async_test_session_local() as db:
        await db.execute(
            text("TRUNCATE TABLE applications RESTART IDENTITY CASCADE")
        )
        await db.execute(
            text("TRUNCATE TABLE users RESTART IDENTITY CASCADE")
        )
        await db.commit()

    yield