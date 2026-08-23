import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.application_service import ApplicationStorage

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_storage():
    ApplicationStorage.applications.clear()

@pytest.fixture
def sample_applications():
    return [
        {
            "id": 1,
            "company": "google",
            "position": "software engineer",
            "status": "offer"
        },
        {
            "id": 2,
            "company": "amazon",
            "position": "backend engineer",
            "status": "applied"
        },
        {
            "id": 3,
            "company": "microsoft",
            "position": "software engineer",
            "status": "interview"
        }
    ]

def test_post_applications(sample_applications):        
    for application in sample_applications:
        response = client.post(
            "/applications",
            json=application
        )
        assert response.status_code == 200
    

def test_duplicate_application(sample_applications):
    for application in sample_applications:
        response = client.post(
            "/applications",
            json=application
        )
        assert response.status_code == 200

    response = client.post(
        "/applications",
        json = {
            "id": 2,
            "company": "amazon",
            "position": "backend engineer",
            "status": "applied"      
        }
    )

    assert response.status_code == 409

def test_get_applications(sample_applications):    
    for application in sample_applications:
        response = client.post(
            "/applications",
            json=application
        )
        assert response.status_code == 200

    response = client.get("/applications")


    assert response.status_code == 200


    data = response.json()


    assert len(data) == 3
    assert data[0]["company"] == "google"
    assert data[1]["company"] == "amazon"
    assert data[2]["company"] == "microsoft"

def test_get_application_id(sample_applications):
    for application in sample_applications:
        response = client.post(
            "/applications",
            json=application
        )
        assert response.status_code == 200


    response = client.get("/applications/2")


    assert response.status_code == 200


    data = response.json()


    assert data["company"] == "amazon"
    assert data["status"] == "applied"

def test_delete_application(sample_applications):
    for application in sample_applications:
        response = client.post(
            "/applications",
            json=application
        )
        assert response.status_code == 200


    response = client.delete("/applications/2")
    assert response.status_code == 200


    response = client.get("/applications")
    assert response.status_code == 200

    
    data = response.json()
    assert len(data) == 2
    assert all(application["id"] != 2 for application in data)


def test_get_missing_application():
    response = client.get("/applications/999")

    assert response.status_code == 404