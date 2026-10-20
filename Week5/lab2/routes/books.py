import base64
import binascii
import json

from flask import Blueprint, jsonify, request
from sqlalchemy import and_, or_

from models import Book, db

books_bp = Blueprint("books_bp", __name__, url_prefix="/api/v1")


@books_bp.get("/books")
def get_books():
    parsed_sort = parse_sort(request.args.get("sort", "id"))
    if parsed_sort is None:
        return jsonify({"error": "Unsupported sort key"}), 400
    sort_key, primary_column, order_columns, descending = parsed_sort

    try:
        limit = int(request.args.get("limit", 20))
        if not 1 <= limit <= 100:
            raise ValueError
        category_id = request.args.get("cat_id")
        if category_id is not None:
            category_id = int(category_id)
    except ValueError:
        return jsonify({"error": "Invalid limit or category id"}), 400

    query = Book.query
    if category_id is not None:
        query = query.filter(Book.category_id == category_id)

    try:
        query = apply_cursor(
            query,
            request.args.get("cursor"),
            sort_key,
            primary_column,
            descending,
        )
    except ValueError:
        return jsonify({"error": "Invalid cursor"}), 400

    books = query.order_by(*order_columns).limit(limit + 1).all()
    return build_response(books, sort_key, descending, limit)


def parse_sort(raw_sort):
    descending = raw_sort.startswith("-")
    key = raw_sort[1:] if descending else raw_sort
    columns = {"id": Book.id, "price": Book.price_vnd}
    primary_column = columns.get(key)
    if primary_column is None:
        return None

    primary_order = primary_column.desc() if descending else primary_column.asc()
    id_order = Book.id.desc() if descending else Book.id.asc()
    return key, primary_column, [primary_order, id_order], descending


def apply_cursor(query, raw_cursor, sort_key, primary_column, descending):
    if not raw_cursor:
        return query

    try:
        padded_cursor = raw_cursor + "=" * (-len(raw_cursor) % 4)
        cursor_bytes = base64.b64decode(
            padded_cursor.encode("ascii"), altchars=b"-_", validate=True
        )
        cursor = json.loads(cursor_bytes.decode("utf-8"))
        cursor_sort = cursor["sort"]
        cursor_value = cursor["value"]
        cursor_id = cursor["id"]
        expected_sort = ("-" if descending else "") + sort_key
        if (
            cursor_sort != expected_sort
            or isinstance(cursor_value, bool)
            or not isinstance(cursor_value, int)
            or isinstance(cursor_id, bool)
            or not isinstance(cursor_id, int)
            or cursor_id < 1
            or (sort_key == "id" and cursor_value != cursor_id)
        ):
            raise ValueError
    except (
        binascii.Error,
        UnicodeEncodeError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ):
        raise ValueError("Invalid cursor") from None

    if sort_key == "id":
        comparison = Book.id < cursor_id if descending else Book.id > cursor_id
        return query.filter(comparison)

    primary_comparison = (
        primary_column < cursor_value if descending else primary_column > cursor_value
    )
    id_comparison = Book.id < cursor_id if descending else Book.id > cursor_id
    return query.filter(
        or_(primary_comparison, and_(primary_column == cursor_value, id_comparison))
    )


def build_response(books, sort_key, descending, limit):
    has_more = len(books) > limit
    page = books[:limit]
    next_cursor = None
    if has_more:
        last_book = page[-1]
        cursor_data = {
            "sort": ("-" if descending else "") + sort_key,
            "value": last_book.id if sort_key == "id" else last_book.price_vnd,
            "id": last_book.id,
        }
        next_cursor = base64.urlsafe_b64encode(
            json.dumps(cursor_data, separators=(",", ":")).encode("utf-8")
        ).decode("ascii").rstrip("=")

    return jsonify({
        "items": [{
            "id": book.id,
            "title": book.title,
            "isbn": book.isbn,
            "price_vnd": book.price_vnd,
            "stock": book.stock,
            "author_id": book.author_id,
            "category_id": book.category_id,
        } for book in page],
        "next_cursor": next_cursor,
    })


@books_bp.get("/books/<int:book_id>")
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify({
        "id": book.id,
        "title": book.title,
        "isbn": book.isbn,
        "price_vnd": book.price_vnd,
        "stock": book.stock,
        "author_id": book.author_id,
        "category_id": book.category_id,
    })


@books_bp.post("/books")
def create_book():
    data = request.get_json(silent=True) or {}
    required = ["title", "isbn", "price_vnd", "author_id", "category_id"]
    missing = [field for field in required if field not in data or data[field] in (None, "")]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    book = Book(
        title=data["title"],
        isbn=data["isbn"],
        price_vnd=data["price_vnd"],
        stock=data.get("stock", 0),
        author_id=data["author_id"],
        category_id=data["category_id"],
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({
        "id": book.id,
        "title": book.title,
        "isbn": book.isbn,
        "price_vnd": book.price_vnd,
        "stock": book.stock,
        "author_id": book.author_id,
        "category_id": book.category_id,
    }), 201


@books_bp.put("/books/<int:book_id>")
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json(silent=True) or {}
    for field in ["title", "isbn", "price_vnd", "stock", "author_id", "category_id"]:
        if field in data:
            setattr(book, field, data[field])
    db.session.commit()
    return jsonify({
        "id": book.id,
        "title": book.title,
        "isbn": book.isbn,
        "price_vnd": book.price_vnd,
        "stock": book.stock,
        "author_id": book.author_id,
        "category_id": book.category_id,
    })


@books_bp.delete("/books/<int:book_id>")
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"})
