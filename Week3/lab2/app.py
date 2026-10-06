from __future__ import annotations

import logging

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

logging.basicConfig(level=logging.ERROR)

RESOURCES = {
    1: {"id": 1, "name": "First resource"},
    2: {"id": 2, "name": "Second resource"},
}


class ProblemError(Exception):
    def __init__(self, status, title, detail, instance=None, type_="about:blank"):
        self.status = status
        self.title = title
        self.detail = detail
        self.instance = instance or request.path
        self.type = type_

    def to_dict(self):
        return {
            "type": self.type,
            "title": self.title,
            "detail": self.detail,
            "status": self.status,
            "instance": self.instance,
        }

    def to_response(self):
        response = jsonify(self.to_dict())
        response.status_code = self.status
        response.headers["Content-Type"] = "application/problem+json"
        return response


def make_problem_response(status, title, detail, instance=None):
    payload = {
        "type": "about:blank",
        "title": title,
        "detail": detail,
        "status": status,
        "instance": instance or request.path,
    }
    response = jsonify(payload)
    response.status_code = status
    response.headers["Content-Type"] = "application/problem+json"
    return response


@app.errorhandler(ProblemError)
def handle_problem_error(error: ProblemError):
    return error.to_response()


@app.errorhandler(HTTPException)
def handle_http_exception(error: HTTPException):
    return make_problem_response(
        error.code or 500,
        error.name,
        error.description or "An error occurred.",
        request.path,
    )


@app.errorhandler(Exception)
def handle_unexpected_error(error: Exception):
    app.logger.exception("Unhandled exception: %s", error)
    return make_problem_response(
        500,
        "Internal Server Error",
        "An unexpected server error occurred. Please try again later.",
        request.path,
    )


@app.get("/")
def home():
    return jsonify({"message": "B2 API is running"})


@app.get("/resources/<int:resource_id>")
def get_resource(resource_id: int):
    resource = RESOURCES.get(resource_id)
    if resource is None:
        raise ProblemError(
            404,
            "Resource not found",
            f"Resource {resource_id} does not exist.",
            request.path,
        )
    return jsonify(resource)


if __name__ == "__main__":
    app.run(debug=False)
