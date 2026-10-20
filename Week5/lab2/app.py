import os

from flask import Flask, jsonify

from models import Author, Book, Category, Review, User, db

app = Flask(__name__)
os.makedirs(app.instance_path, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookstore.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_SORT_KEYS"] = False

db.init_app(app)


@app.get("/")
def home():
    return jsonify({
        "message": "Bookstore API is running",
        "version": "v1",
        "resources": ["/api/v1/books", "/api/v1/books/<int:book_id>"],
    })


from routes.books import books_bp
app.register_blueprint(books_bp)


with app.app_context():
    db.create_all()

    if not Author.query.first():
        db.session.add_all([
            Author(name="Nguyen Van A", bio="Python author"),
            Author(name="Tran Thi B", bio="Web author"),
        ])
        db.session.commit()

    if not Category.query.first():
        db.session.add_all([
            Category(name="Programming", slug="programming"),
            Category(name="Web", slug="web"),
        ])
        db.session.commit()

    if not User.query.first():
        db.session.add_all([
            User(email="user1@example.com", display_name="User One"),
            User(email="user2@example.com", display_name="User Two"),
        ])
        db.session.commit()

    if not Book.query.first():
        db.session.add_all([
            Book(title="Python for Beginners", isbn="9781234567890", price_vnd=250000, stock=10, author_id=1, category_id=1),
            Book(title="Flask API Development", isbn="9781234567891", price_vnd=320000, stock=5, author_id=2, category_id=2),
        ])
        db.session.commit()

    if not Review.query.first():
        db.session.add_all([
            Review(rating=5, book_id=1, user_id=1),
            Review(rating=4, book_id=2, user_id=2),
        ])
        db.session.commit()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
