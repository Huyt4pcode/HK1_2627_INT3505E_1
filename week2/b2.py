from flask import Flask, jsonify, make_response, request


app = Flask(__name__)

BOOKS = []


def find_book_index(bid):
	return next((index for index, book in enumerate(BOOKS) if book["id"] == bid), None)


@app.get("/books/<int:bid>")
def fetch(bid):
	index = find_book_index(bid)
	if index is None:
		return jsonify(error="not found"), 404

	response = make_response(jsonify(BOOKS[index]), 200)
	response.headers["Cache-Control"] = "max-age=60"
	return response


@app.put("/books/<int:bid>")
def put(bid):
	index = find_book_index(bid)
	if index is None:
		return jsonify(error="not found"), 404

	payload = request.get_json(silent=True) or {}
	title = payload.get("title")
	author = payload.get("author")
	if not title or not author:
		return jsonify(error="need title+author"), 422

	BOOKS[index] = {
		"id": bid,
		"title": title.strip(),
		"author": author.strip(),
		"isbn": payload.get("isbn"),
		"price": payload.get("price"),
	}
	return jsonify(BOOKS[index]), 200


@app.patch("/books/<int:bid>")
def patch(bid):
	index = find_book_index(bid)
	if index is None:
		return jsonify(error="not found"), 404

	payload = request.get_json(silent=True) or {}
	if "price" in payload and payload["price"] < 0:
		return jsonify(error="price must be positive"), 422

	for field in "title author isbn price".split():
		if field in payload:
			BOOKS[index][field] = payload[field]
	return jsonify(BOOKS[index]), 200


@app.delete("/books/<int:bid>")
def delete(bid):
	index = find_book_index(bid)
	if index is None:
		return jsonify(error="not found"), 404

	BOOKS.pop(index)
	return "", 204


if __name__ == "__main__":
	app.run(host="127.0.0.1", port=8000, debug=True)
