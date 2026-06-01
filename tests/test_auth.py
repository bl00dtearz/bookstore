import pytest
from app.services.auth import hash_password, verify_password, create_access_token


# ── Unit tests ────────────────────────────────────────────────────────────────

def test_password_hashing():
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"
    assert verify_password("mypassword", hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_access_token():
    token = create_access_token(42)
    assert isinstance(token, str)
    assert len(token) > 10


# ── Integration tests ─────────────────────────────────────────────────────────

def test_register_success(client):
    resp = client.post("/auth/register", json={
        "name": "Bob", "email": "bob@test.com", "password": "bob12345"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "bob@test.com"
    assert data["role"] == "customer"


def test_register_duplicate_email(client, regular_user):
    resp = client.post("/auth/register", json={
        "name": "Alice2", "email": "alice@test.com", "password": "alice1234"
    })
    assert resp.status_code == 400


def test_register_weak_password(client):
    resp = client.post("/auth/register", json={
        "name": "Bob", "email": "bob@test.com", "password": "short"
    })
    assert resp.status_code == 422


def test_login_success(client, regular_user):
    resp = client.post("/auth/login", json={"email": "alice@test.com", "password": "alice1234"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client, regular_user):
    resp = client.post("/auth/login", json={"email": "alice@test.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_me_with_valid_token(client, regular_user):
    token_resp = client.post("/auth/login", json={"email": "alice@test.com", "password": "alice1234"})
    token = token_resp.json()["access_token"]
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@test.com"


def test_me_without_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401
