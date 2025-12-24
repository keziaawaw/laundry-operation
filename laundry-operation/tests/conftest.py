import time
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from auth.jwt_handler import create_token
from auth.repository import user_repository
from main import app


@pytest.fixture(scope="function", autouse=True)
def reset_repository():
    user_repository.users.clear()
    user_repository.users_by_username.clear()
    user_repository.users_by_email.clear()
    yield
    user_repository.users.clear()
    user_repository.users_by_username.clear()
    user_repository.users_by_email.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    timestamp = int(time.time())
    user_data = {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "password123",
        "full_name": "Test User",
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    return user_data


@pytest.fixture
def auth_token(registered_user, client):
    response = client.post(
        "/auth/login", data={"username": registered_user["username"], "password": registered_user["password"]}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def invalid_token():
    return "invalid_token_here"


@pytest.fixture
def expired_token():
    return create_token({"sub": "test_user"}, expires_delta=timedelta(minutes=-1))
