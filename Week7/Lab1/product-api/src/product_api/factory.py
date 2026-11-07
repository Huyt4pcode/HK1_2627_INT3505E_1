import os

from flask import Flask

from .api import products_bp
from .errors import register_error_handlers
from .extensions import db


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///products.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSON_SORT_KEYS"] = False
    if config:
        app.config.update(config)

    db.init_app(app)
    register_error_handlers(app)
    app.register_blueprint(products_bp)

    with app.app_context():
        db.create_all()

    return app
