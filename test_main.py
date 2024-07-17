import pytest
from fastapi.testclient import TestClient
from app import app, get_db, get_test_db

# Override the database dependency with the test database
app.dependency_overrides[get_db] = get_test_db


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_user(client):
    # Test creating a user
    response = client.post("/users/",
                           json={"username": "testuser", "email": "testuser@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

    # Test getting the user
    response = client.get(f"/users/{'testuser@example.com'}/")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

    # Test deleting the user
    response = client.delete(f"/users/{data['id']}/")
    assert response.status_code == 200
    response = client.get(f"/users/{'testuser@example.com'}/")
    assert response.status_code == 404


# def test_create_diary(client):
#     # First, create a user
#     client.post("/users/", json={"username": "testuser", "email": "testuser@example.com", "password": "password123"})
#
#     response = client.post("/diaries/", json={
#         "userId": 1,
#         "date": "2024-07-15",
#         "rawInput": "Sample raw input",
#         "content": "Sample content",
#         "imgUrl": "http://example.com/image.jpg"
#     })
#     assert response.status_code == 200
#     data = response.json()
#     assert data["userId"] == 1
#     assert data["date"] == "2024-07-15"
#     assert data["rawInput"] == "Sample raw input"
#     assert data["content"] == "Sample content"
#     assert data["imgUrl"] == "http://example.com/image.jpg"
