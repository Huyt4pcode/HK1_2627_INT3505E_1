import hashlib
import json

from flask import Flask, jsonify, make_response, request


app = Flask(__name__)

BOOKS = [
	{"id": 1, "title": "Python cơ bản", "author": "DAO QUANG HUY", "isbn": "123456", "price": 100000},
]


def calculate_etag(book):
	content = {key: value for key, value in book.items() if key != "etag"}
	serialized = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
	digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
	return f'"{digest}"'


def refresh_etag(book):
	book["etag"] = calculate_etag(book)


for book in BOOKS:
	refresh_etag(book)


def find_book(bid):
	return next((book for book in BOOKS if book["id"] == bid), None)


@app.get("/books/<int:bid>")
def get_book(bid):
	book = find_book(bid)
	if book is None:
		return jsonify(error="not found"), 404

	response = make_response(jsonify(book), 200)
	response.headers["ETag"] = book["etag"]
	response.headers["Cache-Control"] = "max-age=60"

	if request.if_none_match.contains(book["etag"]):
		response.status_code = 304
		response.set_data(b"")

	return response


@app.put("/books/<int:bid>")
def update_book(bid):
	book = find_book(bid)
	if book is None:
		return jsonify(error="not found"), 404

	payload = request.get_json(silent=True) or {}
	title = (payload.get("title") or "").strip()
	author = (payload.get("author") or "").strip()
	if not title or not author:
		return jsonify(error="need title+author"), 422

	book.update({
		"title": title,
		"author": author,
		"isbn": payload.get("isbn"),
		"price": payload.get("price"),
	})
	refresh_etag(book)
	response = make_response(jsonify(book), 200)
	response.headers["ETag"] = book["etag"]
	return response


if __name__ == "__main__":
	app.run(host="127.0.0.1", port=8000, debug=True)
