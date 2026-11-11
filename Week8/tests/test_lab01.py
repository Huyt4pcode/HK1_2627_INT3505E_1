"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""


"""LAB 1 — Book API tests."""

from copy import deepcopy

import pytest
from jsonschema import validate, ValidationError
from tools import get_book_schema


def test_get_books_empty_database(client):
    response = client.get("/books")

    assert response.status_code == 200
    assert response.get_json() == []


def test_get_nonexistent_book(client):
    response = client.get("/books/9999")

    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"


def test_create_book_missing_title(client):
    response = client.post(
        "/books",
        json={"author": "John Doe"}
    )

    assert response.status_code == 400

    errors = response.get_json()["errors"]

    assert any(error["field"] == "title" for error in errors)


def test_create_delete_and_get_book(client, sample_book):
    create_response = client.post("/books", json=sample_book)

    assert create_response.status_code == 201

    book_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/books/{book_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/books/{book_id}")

    assert get_response.status_code == 404


def test_book_response_json_schema(client, sample_book):
    response = client.post("/books", json=sample_book)

    assert response.status_code == 201

    book_data = response.get_json()

    schema = get_book_schema()

    validate(instance=book_data, schema=schema)

    invalid_book = deepcopy(book_data)
    invalid_book["unknown_field"] = "unexpected"

    with pytest.raises(ValidationError):
        validate(instance=invalid_book, schema=schema)
