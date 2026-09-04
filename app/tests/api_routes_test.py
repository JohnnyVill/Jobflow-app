import pytest
import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from sqlalchemy import text, select
from sqlalchemy.orm import undefer
from app.db.database import async_test_session_local, get_db, User
from app.main import app

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

#Data used to every application test
@pytest.fixture
def sample_applications():
    return [
        {
            "company": "google",
            "position": "software engineer",
            "status": "offer"
        },
        {

            "company": "amazon",
            "position": "backend engineer",
            "status": "applied"
        },
        {
            "company": "microsoft",
            "position": "software engineer",
            "status": "interview"
        }
    ]

#Data used for every user test
@pytest.fixture
def sample_users():
    return [
        {
            "email": "joe@gmail.com",
            "password": "softwareengineer",
        },
        {

            "email": "doe@yahoo.com",
            "password": "backendengineer",
        },
        {
            "email": "jane@gmail.com",
            "password": "frontendengineer",
        }
    ]


async def test_registration(client, sample_users):
    plaintext_password = "softwareengineer"
    for user in sample_users:
        response = await client.post(
            "/auth/register",
            json=user
        )
        assert response.status_code == 200
        data = response.json()

        assert "password" not in data
        assert "password_hash" not in data
    
    async with async_test_session_local() as db:
        result = await db.execute(
            select(User)
            .options(undefer(User.password_hash))
            .where(User.email == "joe@gmail.com")
        )
        stored_user = result.scalar_one()

        assert stored_user.password_hash != plaintext_password
        assert stored_user.password_hash.startswith("$2")
        assert stored_user.check_password(plaintext_password) is True
        assert stored_user.check_password("wrong_password") is False

async def test_login(client, sample_users):
    for user in sample_users:
        response = await client.post(
            "/auth/register",
            json=user
        )
        assert response.status_code == 200
    user_login = {
        "email": "joe@gmail.com",
        "password": "softwareengineer",
    }
    login = await client.post(
        "/auth/login",
        json=user_login
    )
    assert login.status_code == 200
    data = login.json()
    assert user_login["email"] == data["email"]


async def test_duplicate_email(client, sample_users):
    for user in sample_users:
        response = await client.post(
            "/auth/register",
            json=user
        )
        assert response.status_code == 200

    #test duplicate

    duplicate = await client.post(
        "/auth/register",
        json= {
        
            "email": "doe@yahoo.com",
            "password": "backendengineer",
        }
    )
    assert duplicate.status_code == 409
    
async def test_post_applications(client, sample_applications):        
    for application in sample_applications:
        response = await client.post(
            "/applications",
            json=application
        )
        assert response.status_code == 200


async def test_duplicate_application(client, sample_applications):
    #populate table with data
    for application in sample_applications:
        response = await client.post(
            "/applications",
            json=application
        )
        assert response.status_code == 200


    #test            
    response = await client.post(
        "/applications",
        json = {
            "company": "amazon",
            "position": "backend engineer",
            "status": "applied"      
        }
    )

    assert response.status_code == 409

async def test_get_applications(client, sample_applications):
    #populate table with data
    for application in sample_applications:
        response = await client.post(
            "/applications",
            json=application
        )
        assert response.status_code == 200    
    response = await client.get("/applications")


    #test
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(sample_applications)

async def test_get_application_id(client, sample_applications):
    #populate table with data
    for application in sample_applications:
        response = await client.post(
            "/applications",
            json=application
        )
        assert response.status_code == 200

    #test
    get_id = await client.get("applications")
    data_id = get_id.json()

    response = await client.get(f"/applications/{data_id[0]["id"]}")


    assert response.status_code == 200
    data = response.json()
    assert data["company"] == data_id[0]["company"]
    assert data["status"] == data_id[0]["status"]

async def test_delete_application(client, sample_applications):
    #populate table with data
    for application in sample_applications:
        response = await client.post(
            "/applications",
            json=application
        )
        assert response.status_code == 200


    #test
    get_id = await client.get("applications")
    data_id = get_id.json()

    response = await client.delete(f"/applications/{data_id[0]["id"]}")
    delete = await client.get("applications")

    post_delete = delete.json()
    assert response.status_code == 200

    assert len(post_delete) == len(sample_applications) - 1
    assert all(
        application["id"] != data_id[0]["id"]
        for application in post_delete
    )
    


async def test_get_missing_application(client):
    response = await client.get("/applications/999")

    assert response.status_code == 404


async def test_delete_nonexisting_application(client):
    response = await client.delete("/applications/999")
    assert response.status_code == 404


async def test_invalid_application(client):
    response = await client.post(
        "/applications",
        json={
            "company":"good vibes",
            "position":"vibe cordinator",
            "status":"lost"
        }
    )

    assert response.status_code ==  422