import json
import os
import sqlite3

from flask import Flask, jsonify, make_response, request


app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(__file__), "orders.db")


def get_db():
	connection = sqlite3.connect(DATABASE)
	connection.row_factory = sqlite3.Row
	return connection


def init_db():
	with get_db() as connection:
		connection.execute(
			"""
			CREATE TABLE IF NOT EXISTS orders (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				payload TEXT NOT NULL
			)
			"""
		)


def order_from_row(row):
	order = json.loads(row["payload"])
	order["id"] = row["id"]
	return order


init_db()


@app.get("/orders")
def list_orders():
	with get_db() as connection:
		rows = connection.execute(
			"SELECT id, payload FROM orders ORDER BY id"
		).fetchall()

	orders = [order_from_row(row) for row in rows]
	return jsonify({"data": orders, "total": len(orders)}), 200


@app.get("/orders/<int:oid>")
def get_order(oid):
	with get_db() as connection:
		row = connection.execute(
			"SELECT id, payload FROM orders WHERE id = ?", (oid,)
		).fetchone()

	if row is None:
		return jsonify(error="order not found"), 404

	return jsonify(order_from_row(row)), 200


@app.post("/orders")
def create_order():
	if not request.is_json:
		return jsonify(error="expected JSON"), 415

	payload = request.get_json(silent=True)
	if not isinstance(payload, dict):
		return jsonify(error="JSON object required"), 422

	with get_db() as connection:
		cursor = connection.execute(
			"INSERT INTO orders (payload) VALUES (?)",
			(json.dumps(payload, ensure_ascii=False),),
		)
		order_id = cursor.lastrowid

	order = dict(payload)
	order["id"] = order_id
	response = make_response(jsonify(order), 201)
	response.headers["Location"] = f"/orders/{order_id}"
	return response


if __name__ == "__main__":
	app.run(host="127.0.0.1", port=8000, debug=True)
