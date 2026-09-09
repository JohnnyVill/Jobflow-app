import pytest
import jwt
from sqlalchemy import select
from sqlalchemy.orm import undefer
from datetime import datetime, timedelta, timezone


from app.db.database import User
from app.tests.conftest import async_test_session_local
from app.core.security import key, token_algorithm


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
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0

async def test_incorrect_login(client, sample_users):
    for user in sample_users:
        response = await client.post(
            "/auth/register",
            json=user
        )
        assert response.status_code == 200
    user_login = {
        "email": "joe@gmail.com",
        "password": "softengineer",
    }
    login = await client.post(
        "/auth/login",
        json=user_login
    )
    assert login.status_code == 401
    assert login.json()["detail"] == "Invalid email or password"
    

async def test_nonuser_login(client, sample_users):
    for user in sample_users:
        response = await client.post(
            "/auth/register",
            json=user
        )
        assert response.status_code == 200
    user_login = {
        "email": "jill@gmail.com",
        "password": "softwareengineer",
    }
    login = await client.post(
        "/auth/login",
        json=user_login
    )
    assert login.status_code == 401
    data = login.json()
    assert data == {
        "detail": "Invalid email or password"
    }

async def test_missing_token(client):
    response = await client.get("/auth/me")

    assert response.status_code == 401

async def test_malformed_token(client):
    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer this-is-not-a-valid-token"
        }
    )

    assert response.status_code == 401

async def test_get_user(client, sample_users):
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
    token = login.json()["access_token"]
    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == "joe@gmail.com"


async def test_expired_token(client, sample_users):
    expired_payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
    }

    expired_token = jwt.encode(
        expired_payload,
        key,
        algorithm=token_algorithm
    )

    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {expired_token}"
        }
    )

    assert response.status_code == 401


async def test_unknown_subject(client, sample_users):
    payload = {
        "sub": "99999",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    token = jwt.encode(
        payload,
        key,
        algorithm=token_algorithm
    )

    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 401

    
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