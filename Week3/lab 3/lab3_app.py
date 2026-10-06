from __future__ import annotations

import base64
import json

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

ORDERS = [
    {"id": 1, "customer_id": 1, "status": "paid", "total": 125.50, "created_at": "2026-09-01T09:00:00Z"},
    {"id": 2, "customer_id": 2, "status": "pending", "total": 80.00, "created_at": "2026-09-02T10:30:00Z"},
    {"id": 3, "customer_id": 1, "status": "paid", "total": 245.00, "created_at": "2026-09-03T11:15:00Z"},
    {"id": 4, "customer_id": 3, "status": "shipped", "total": 59.99, "created_at": "2026-09-04T13:45:00Z"},
    {"id": 5, "customer_id": 2, "status": "paid", "total": 310.25, "created_at": "2026-09-05T08:20:00Z"},
    {"id": 6, "customer_id": 1, "status": "pending", "total": 42.75, "created_at": "2026-09-06T16:10:00Z"},
    {"id": 7, "customer_id": 3, "status": "paid", "total": 175.00, "created_at": "2026-09-07T12:05:00Z"},
    {"id": 8, "customer_id": 2, "status": "shipped", "total": 99.95, "created_at": "2026-09-08T14:25:00Z"},
]

ORDER_FIELDS = set(ORDERS[0])
SORT_FIELDS = {"id", "customer_id", "status", "total", "created_at"}
DEFAULT_LIMIT = 5
MAX_LIMIT = 100


def problem_response(status: int, title: str, detail: str):
    response = jsonify({
        "type": "about:blank",
        "title": title,
        "detail": detail,
        "status": status,
        "instance": request.path,
    })
    response.status_code = status
    response.headers["Content-Type"] = "application/problem+json"
    return response


def encode_cursor(payload: dict) -> str:
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(encoded).decode("ascii").rstrip("=")


def decode_cursor(cursor: str) -> dict:
    try:
        padded_cursor = cursor + "=" * (-len(cursor) % 4)
        decoded = base64.b64decode(
            padded_cursor,
            altchars=b"-_",
            validate=True,
        )
        payload = json.loads(decoded)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("cursor must be a valid cursor returned by this endpoint") from None

    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("cursor must be a valid cursor returned by this endpoint")
    return payload


@app.get("/")
def home():
    return jsonify({
        "message": "Lab 3 orders API is running",
        "endpoint": "/orders",
        "query_parameters": ["cursor", "limit", "status", "customer_id", "sort", "fields"],
    })


@app.get("/orders")
def get_orders():
    raw_limit = request.args.get("limit", str(DEFAULT_LIMIT))
    try:
        limit = int(raw_limit)
    except ValueError:
        return problem_response(400, "Invalid limit", "limit must be an integer.")
    if not 1 <= limit <= MAX_LIMIT:
        return problem_response(
            400,
            "Invalid limit",
            f"limit must be between 1 and {MAX_LIMIT}.",
        )

    status = request.args.get("status")
    raw_customer_id = request.args.get("customer_id")
    customer_id = None
    if raw_customer_id is not None:
        try:
            customer_id = int(raw_customer_id)
        except ValueError:
            return problem_response(400, "Invalid customer_id", "customer_id must be an integer.")

    raw_sort = request.args.get("sort", "id")
    descending = raw_sort.startswith("-")
    sort_field = raw_sort[1:] if descending else raw_sort
    if sort_field not in SORT_FIELDS:
        return problem_response(
            400,
            "Invalid sort",
            f"sort must be one of: {', '.join(sorted(SORT_FIELDS))}, optionally prefixed with '-'.",
        )

    raw_fields = request.args.get("fields")
    selected_fields = None
    if raw_fields is not None:
        selected_fields = {field.strip() for field in raw_fields.split(",") if field.strip()}
        if not selected_fields:
            return problem_response(400, "Invalid fields", "fields must contain at least one field.")
        unknown_fields = selected_fields - ORDER_FIELDS
        if unknown_fields:
            return problem_response(
                400,
                "Invalid fields",
                f"Unknown order fields: {', '.join(sorted(unknown_fields))}.",
            )

    filtered_orders = [
        order
        for order in ORDERS
        if (status is None or order["status"] == status)
        and (customer_id is None or order["customer_id"] == customer_id)
    ]
    filtered_orders.sort(
        key=lambda order: (order[sort_field], order["id"]),
        reverse=descending,
    )

    if "cursor" in request.args:
        try:
            cursor_data = decode_cursor(request.args["cursor"])
        except ValueError as error:
            return problem_response(400, "Invalid cursor", str(error))

        expected_query = {
            "sort": raw_sort,
            "status": status,
            "customer_id": customer_id,
        }
        if any(cursor_data.get(key) != value for key, value in expected_query.items()):
            return problem_response(400, "Invalid cursor", "cursor does not match the current filters or sort.")

        last_id = cursor_data.get("last_id")
        last_value = cursor_data.get("last_value")
        cursor_index = next(
            (
                index
                for index, order in enumerate(filtered_orders)
                if order["id"] == last_id and order[sort_field] == last_value
            ),
            None,
        )
        if cursor_index is None:
            return problem_response(400, "Invalid cursor", "cursor points to an order that does not exist.")
        filtered_orders = filtered_orders[cursor_index + 1 :]

    page = filtered_orders[:limit]
    has_more = len(filtered_orders) > limit
    next_cursor = None
    if has_more and page:
        last_order = page[-1]
        next_cursor = encode_cursor({
            "version": 1,
            "sort": raw_sort,
            "status": status,
            "customer_id": customer_id,
            "last_id": last_order["id"],
            "last_value": last_order[sort_field],
        })

    data = [
        {key: value for key, value in order.items() if selected_fields is None or key in selected_fields}
        for order in page
    ]
    return jsonify({
        "data": data,
        "pagination": {
            "limit": limit,
            "next_cursor": next_cursor,
        },
    })


if __name__ == "__main__":
    app.run(debug=False)
