def create_product(client, **overrides):
    product = {
        "sku": "DEMO-001",
        "name": "Demo product",
        "price_cents": 1299,
        "qty_in_stock": 5,
    }
    product.update(overrides)
    return client.post("/api/v1/products", json=product)


def test_list_products_returns_products(client):
    created = create_product(client)

    response = client.get("/api/v1/products")

    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == created.get_json()["id"]
    assert body["items"][0]["sku"] == "DEMO-001"


def test_create_product_returns_created_product(client):
    response = create_product(client)

    assert response.status_code == 201
    body = response.get_json()
    assert body["sku"] == "DEMO-001"
    assert body["name"] == "Demo product"
    assert body["price_cents"] == 1299
    assert body["qty_in_stock"] == 5


def test_create_product_rejects_missing_required_field(client):
    response = client.post(
        "/api/v1/products",
        json={"sku": "DEMO-001", "name": "Demo product"},
    )

    assert response.status_code == 422
    assert response.get_json()["code"] == "validation_error"


def test_create_product_rejects_duplicate_sku(client):
    first = create_product(client)
    duplicate = create_product(client, name="Another product")

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.get_json()["code"] == "conflict"


def test_get_product_returns_product(client):
    created = create_product(client)
    product_id = created.get_json()["id"]

    response = client.get(f"/api/v1/products/{product_id}")

    assert response.status_code == 200
    assert response.get_json()["sku"] == "DEMO-001"


def test_patch_product_updates_fields(client):
    created = create_product(client)
    product_id = created.get_json()["id"]

    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={"name": "Updated product", "price_cents": 1500},
    )

    assert response.status_code == 200
    assert response.get_json()["name"] == "Updated product"
    assert response.get_json()["price_cents"] == 1500


def test_reserve_product_decreases_stock(client):
    created = create_product(client)
    product_id = created.get_json()["id"]

    response = client.post(
        f"/api/v1/products/{product_id}/reserve",
        json={"qty": 2},
    )

    assert response.status_code == 200
    assert response.get_json()["qty_in_stock"] == 3


def test_reserve_product_rejects_insufficient_stock(client):
    created = create_product(client)
    product_id = created.get_json()["id"]

    response = client.post(
        f"/api/v1/products/{product_id}/reserve",
        json={"qty": 6},
    )

    assert response.status_code == 409
    assert response.get_json()["code"] == "out_of_stock"


def test_delete_product_archives_it(client):
    created = create_product(client)
    product_id = created.get_json()["id"]

    response = client.delete(f"/api/v1/products/{product_id}")
    get_response = client.get(f"/api/v1/products/{product_id}")
    list_response = client.get("/api/v1/products")

    assert response.status_code == 204
    assert get_response.status_code == 404
    assert list_response.get_json()["total"] == 0
