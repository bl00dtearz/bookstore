from tests.conftest import get_token


def test_get_empty_cart(client, regular_user):
    token = get_token(client, "alice@test.com", "alice1234")
    resp = client.get("/cart", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["items"] == []
    assert resp.json()["total"] == 0.0


def test_add_to_cart(client, regular_user, sample_book):
    token = get_token(client, "alice@test.com", "alice1234")
    resp = client.post("/cart/items",
                       json={"book_id": sample_book.id, "quantity": 2},
                       headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert data["total"] == round(9.99 * 2, 2)


def test_add_out_of_stock(client, regular_user, sample_book):
    token = get_token(client, "alice@test.com", "alice1234")
    resp = client.post("/cart/items",
                       json={"book_id": sample_book.id, "quantity": 999},
                       headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400


def test_place_order_full_flow(client, regular_user, sample_book, db):
    token = get_token(client, "alice@test.com", "alice1234")

    # Add to cart
    client.post("/cart/items",
                json={"book_id": sample_book.id, "quantity": 1},
                headers={"Authorization": f"Bearer {token}"})

    # Place order
    resp = client.post("/orders",
                       json={"shipping_address": "123 Main St"},
                       headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    order = resp.json()
    assert order["total_price"] == 9.99
    assert order["status"] == "paid"
    assert len(order["items"]) == 1

    # Cart should be empty after order
    cart = client.get("/cart", headers={"Authorization": f"Bearer {token}"})
    assert cart.json()["items"] == []

    # Stock should decrease
    db.refresh(sample_book)
    assert sample_book.stock == 9


def test_place_order_empty_cart(client, regular_user):
    token = get_token(client, "alice@test.com", "alice1234")
    resp = client.post("/orders", json={}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400


def test_list_orders(client, regular_user, sample_book):
    token = get_token(client, "alice@test.com", "alice1234")
    client.post("/cart/items", json={"book_id": sample_book.id, "quantity": 1},
                headers={"Authorization": f"Bearer {token}"})
    client.post("/orders", json={}, headers={"Authorization": f"Bearer {token}"})

    resp = client.get("/orders", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
