from flask import Blueprint

products_bp = Blueprint("products", __name__, url_prefix="/api/v1")

from . import products  # noqa: E402,F401
