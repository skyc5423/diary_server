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


def test_create_diary(client):
    # First, create a user
    random_id = "fjiafdsfffl"
    response_user = client.post("/users/",
                                json={"username": "testuser",
                                      "email": f"{random_id}@example.com",
                                      "password": "password123"})
    assert response_user.status_code == 200
    data_user = response_user.json()
    assert data_user["username"] == "testuser"
    assert data_user["email"] == f"{random_id}@example.com"

    response = client.post("/diaries/", json={
        "userId": data_user["id"],
        "date": "2024-07-15",
        "rawInput": "강남, 친구, 술",
    })
    assert response.status_code == 200
    data_diary = response.json()
    assert data_diary["userId"] == data_user["id"]
    assert data_diary["date"] == "2024-07-15"
    assert data_diary["rawInput"] == "강남, 친구, 술"

    # Test getting the diary
    response = client.get(f"/users/{data_user['id']}/diaries/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["userId"] == data_user["id"]
    assert data[0]["date"] == "2024-07-15"
    assert data[0]["rawInput"] == "강남, 친구, 술"
    assert data[0]["content"] == data_diary["content"]
    # assert data[0]["imgUrl"] == "http://example.com/image.jpg"
    # assert data[0]["isValid"] == True
    assert data[0]["id"] == data_diary["id"]

    # Test deleting the diary
    response = client.delete(f"/diaries/{data_diary['id']}/")
    assert response.status_code == 200
    response = client.get(f"/users/{data_user['id']}/diaries/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

    # Test deleting the user
    response = client.delete(f"/users/{data_user['id']}/")
    assert response.status_code == 200
    response = client.get(f"/users/{random_id}@example.com/")
    assert response.status_code == 404
