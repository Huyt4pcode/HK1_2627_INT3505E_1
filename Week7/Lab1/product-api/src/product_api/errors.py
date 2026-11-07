from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify(error="Validation failed", detail=error.messages), 422

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify(error="Not found", detail=error.description), 404

    @app.errorhandler(409)
    def handle_conflict(error):
        return jsonify(error="Conflict", detail=error.description), 409

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify(error=error.name, detail=error.description), error.code
