from flask import abort, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Product
from ..schemas import ProductCreateSchema, ProductUpdateSchema, ReserveSchema
from . import products_bp


def product_json(product):
    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "price_cents": product.price_cents,
        "qty_in_stock": product.qty_in_stock,
        "archived": product.archived,
    }


def parse_json():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        raise ValidationError({"json": ["A JSON object is required"]})
    return data


@products_bp.get("/products")
def list_products():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 20))
    except ValueError:
        raise ValidationError({"query": ["page and size must be integers"]})
    if page < 1 or size < 1 or size > 100:
        raise ValidationError({"query": ["page must be >= 1 and size must be between 1 and 100"]})

    archived = request.args.get("archived", "false").lower()
    if archived not in {"true", "false"}:
        raise ValidationError({"archived": ["must be true or false"]})

    query = Product.query.filter_by(archived=(archived == "true"))
    total = query.count()
    products = query.order_by(Product.id.asc()).offset((page - 1) * size).limit(size).all()
    return jsonify(items=[product_json(product) for product in products], page=page, size=size, total=total)


@products_bp.get("/products/<int:product_id>")
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None or product.archived:
        abort(404, description="Product not found")
    return jsonify(product_json(product))


@products_bp.post("/products")
def create_product():
    data = ProductCreateSchema().load(parse_json())
    product = Product(**data)
    db.session.add(product)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(409, description="SKU already exists")
    return jsonify(product_json(product)), 201


@products_bp.patch("/products/<int:product_id>")
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None or product.archived:
        abort(404, description="Product not found")
    data = ProductUpdateSchema().load(parse_json())
    for field, value in data.items():
        setattr(product, field, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(409, description="SKU already exists")
    return jsonify(product_json(product))


@products_bp.post("/products/<int:product_id>/reserve")
def reserve_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None or product.archived:
        abort(404, description="Product not found")
    qty = ReserveSchema().load(parse_json())["qty"]
    if qty > product.qty_in_stock:
        return jsonify(error="Insufficient stock", detail="qty_in_stock is not enough"), 409
    product.qty_in_stock -= qty
    db.session.commit()
    return jsonify(product_json(product))


@products_bp.delete("/products/<int:product_id>")
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None or product.archived:
        abort(404, description="Product not found")
    product.archived = True
    db.session.commit()
    return jsonify(message="Product archived successfully"), 200
