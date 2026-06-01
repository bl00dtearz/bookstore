from tests.conftest import get_token


def test_list_reviews_empty(client, sample_book):
    resp = client.get(f"/books/{sample_book.id}/reviews")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_review(client, regular_user, sample_book):
    token = get_token(client, "alice@test.com", "alice1234")
    resp = client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 4.5, "comment": "Great book!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["rating"] == 4.5
    assert data["comment"] == "Great book!"
    assert data["user_name"] == "Alice"


def test_create_review_invalid_rating(client, regular_user, sample_book):
    token = get_token(client, "alice@test.com", "alice1234")
    resp = client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 6.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


def test_duplicate_review_blocked(client, regular_user, sample_book):
    token = get_token(client, "alice@test.com", "alice1234")
    client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 3.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 5.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400


def test_delete_own_review(client, regular_user, sample_book):
    token = get_token(client, "alice@test.com", "alice1234")
    create_resp = client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 2.0, "comment": "Not great"},
        headers={"Authorization": f"Bearer {token}"},
    )
    review_id = create_resp.json()["id"]
    resp = client.delete(
        f"/books/{sample_book.id}/reviews/{review_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204


def test_delete_other_users_review_forbidden(client, regular_user, admin_user, sample_book):
    alice_token = get_token(client, "alice@test.com", "alice1234")
    create_resp = client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 5.0},
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    review_id = create_resp.json()["id"]

    admin_token = get_token(client, "admin@test.com", "admin1234")
    resp = client.delete(
        f"/books/{sample_book.id}/reviews/{review_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 403


def test_review_on_nonexistent_book(client, regular_user):
    token = get_token(client, "alice@test.com", "alice1234")
    resp = client.post(
        "/books/9999/reviews",
        json={"rating": 3.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_average_rating_appears_in_book(client, regular_user, sample_book):
    token = get_token(client, "alice@test.com", "alice1234")
    client.post(
        f"/books/{sample_book.id}/reviews",
        json={"rating": 4.0, "comment": "Good"},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = client.get(f"/books/{sample_book.id}")
    assert resp.status_code == 200
    assert resp.json()["average_rating"] == 4.0
