import pytest
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from unittest.mock import Mock
from app.services import user_services


import app.routes.user_routes as ur

# Build FastAPI router inside a mini app for testing
from fastapi import FastAPI
app = FastAPI()
app.include_router(ur.router)
client = TestClient(app)


@pytest.fixture(autouse=True)
def patch_services(monkeypatch):
    """Mock all user service dependencies for all tests."""
    monkeypatch.setattr(ur.user_services, "get_user_by_email", Mock())
    monkeypatch.setattr(ur.user_services, "create_user", Mock())
    monkeypatch.setattr(ur.user_services, "authenticate_user", Mock())
    monkeypatch.setattr(ur.user_services, "create_access_token", Mock(return_value="fake-token"))
    monkeypatch.setattr(ur.user_services, "get_current_user", Mock())

    app.dependency_overrides[user_services.get_current_user] = lambda: {"email": "me@x.com"}

    yield
    app.dependency_overrides = {}



def test_register_user_success(monkeypatch):
    """Should register a new user successfully."""
    fake_user = {"id": 1, "email": "new@x.com"}
    ur.user_services.get_user_by_email.return_value = None
    ur.user_services.create_user.return_value = fake_user

    resp = client.post("/users/register", json={"email": "new@x.com", "password": "123"})
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json() == fake_user
    ur.user_services.create_user.assert_called_once()


def test_register_user_email_exists(monkeypatch):
    """Should raise 400 if email already exists."""
    ur.user_services.get_user_by_email.return_value = {"email": "dup@x.com"}

    resp = client.post("/users/register", json={"email": "dup@x.com", "password": "123"})
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in resp.text


def test_login_success(monkeypatch):
    """Should return access token when valid credentials."""
    ur.user_services.authenticate_user.return_value = {"id": 1, "email": "user@x.com"}
    ur.user_services.create_access_token.return_value = "token123"

    data = {"username": "user@x.com", "password": "pass"}
    resp = client.post("/users/login", data=data)
    assert resp.status_code == 200
    assert resp.json() == {"access_token": "token123", "token_type": "bearer"}


def test_login_invalid_credentials(monkeypatch):
    """Should reject wrong password or user not found."""
    ur.user_services.authenticate_user.return_value = None

    data = {"username": "bad@x.com", "password": "wrong"}
    resp = client.post("/users/login", data=data)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in resp.text
