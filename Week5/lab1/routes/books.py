from flask import Blueprint, jsonify, request

from models import Book, db

books_bp = Blueprint("books_bp", __name__, url_prefix="/api/v1")


@books_bp.get("/books")
def get_books():
    books = Book.query.all()
    payload = []
    for book in books:
        payload.append({
            "id": book.id,
            "title": book.title,
            "isbn": book.isbn,
            "price_vnd": book.price_vnd,
            "stock": book.stock,
            "author_id": book.author_id,
            "category_id": book.category_id,
        })
    return jsonify(payload)


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
