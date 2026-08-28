import pytest

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.main import app



@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client

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

def test_post_applications(client, sample_applications):        
    for application in sample_applications:
        response = client.post(
            "/applications",
            json=application
        )
        assert response.status_code == 200
    

def test_duplicate_application(client):
    response = client.post(
        "/applications",
        json = {
            "company": "amazon",
            "position": "backend engineer",
            "status": "applied"      
        }
    )

    assert response.status_code == 409

def test_get_applications(client):    
    response = client.get("/applications")


    assert response.status_code == 200
    count = client.get("/applications")

    expected_total_count = count.json()
    data = response.json()

    assert len(data) == len(expected_total_count)

def test_get_application_id(client):
    get_id = client.get("applications")
    data_id = get_id.json()

    response = client.get(f"/applications/{data_id[0]["id"]}")


    assert response.status_code == 200


    data = response.json()


    assert data["company"] == data_id[0]["company"]
    assert data["status"] == data_id[0]["status"]

def test_delete_application(client):
    get_id = client.get("applications")
    data_id = get_id.json()

    response = client.delete(f"/applications/{data_id[0]["id"]}")
    delete = client.get("applications")

    post_delete = delete.json()
    assert response.status_code == 200

    assert len(data_id) != len(post_delete)
    


def test_get_missing_application(client):
    response = client.get("/applications/999")

    assert response.status_code == 404


def test_delete_nonexisting_application(client):
    response = client.delete("/applications/999")
    assert response.status_code == 404


def test_invalid_application(client):
    response = client.post(
        "/applications",
        json={
            "company":"good vibes",
            "position":"vibe cordinator",
            "status":"lost"
        }
    )

    assert response.status_code ==  422