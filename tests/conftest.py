"""
Test configuration: uses an isolated in-memory SQLite database.
No real PostgreSQL needed — all tests run standalone.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.models.book import Author, Genre, Book
from app.services.auth import hash_password

TEST_DB_URL = "sqlite:///./test_bookstore.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create fresh tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db):
    user = User(name="Admin", email="admin@test.com",
                password_hash=hash_password("admin1234"), role=UserRole.admin)
    db.add(user); db.commit(); db.refresh(user)
    return user


@pytest.fixture()
def regular_user(db):
    user = User(name="Alice", email="alice@test.com",
                password_hash=hash_password("alice1234"))
    db.add(user); db.commit(); db.refresh(user)
    return user


@pytest.fixture()
def sample_book(db):
    author = Author(name="Test Author")
    genre = Genre(name="Fiction")
    db.add_all([author, genre]); db.flush()
    book = Book(title="Test Book", price=9.99, stock=10, author=author, genres=[genre])
    db.add(book); db.commit(); db.refresh(book)
    return book


def get_token(client, email, password):
    resp = client.post("/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]
