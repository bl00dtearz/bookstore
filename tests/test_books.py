import pytest
from tests.conftest import get_token


def test_list_books_empty(client):
    resp = client.get("/books")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_books_with_data(client, sample_book):
    resp = client.get("/books")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Test Book"


def test_get_book_by_id(client, sample_book):
    resp = client.get(f"/books/{sample_book.id}")
    assert resp.status_code == 200
    assert resp.json()["price"] == 9.99


def test_get_book_not_found(client):
    resp = client.get("/books/9999")
    assert resp.status_code == 404


def test_search_books(client, sample_book):
    resp = client.get("/books?search=Test")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = client.get("/books?search=NoMatch")
    assert resp.status_code == 200
    assert resp.json() == []


def test_filter_by_price(client, sample_book):
    resp = client.get("/books?max_price=5.00")
    assert resp.status_code == 200
    assert resp.json() == []

    resp = client.get("/books?max_price=20.00")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_create_book_as_admin(client, admin_user, db):
    from app.models.book import Author, Genre
    author = Author(name="New Author")
    genre = Genre(name="Sci-Fi")
    db.add_all([author, genre]); db.commit()

    token = get_token(client, "admin@test.com", "admin1234")
    resp = client.post("/books", json={
        "title": "New Book", "price": 19.99, "stock": 5,
        "author_id": author.id, "genre_ids": [genre.id]
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json()["title"] == "New Book"


def test_create_book_as_customer_forbidden(client, regular_user):
    token = get_token(client, "alice@test.com", "alice1234")
    resp = client.post("/books", json={"title": "Hack", "price": 1.0},
                       headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_delete_book_as_admin(client, admin_user, sample_book):
    token = get_token(client, "admin@test.com", "admin1234")
    resp = client.delete(f"/books/{sample_book.id}",
                         headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 204

    resp = client.get(f"/books/{sample_book.id}")
    assert resp.status_code == 404
