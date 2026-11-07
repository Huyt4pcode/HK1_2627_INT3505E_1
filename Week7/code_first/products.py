from flask.views import MethodView
from flask_smorest import Blueprint, abort

from .extensions import db
from .models import Product
from .schemas import ProductInSchema, ProductSchema


blp = Blueprint("products",__name__, url_prefix="products")

class ProductList(MethodView):
    @blp.arguments(ProductInSchema)
    @blp.response(201, ProductSchema)
    def post(self, product_data):
        product = Product(**product_data)
        db.session.add(product)
        db.session.commit()
        return product

    
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        return db.session.execute.(db.select(Product)).scalars().all()

    @blp.add_url_rule("/", view_func=ProductList.as_view("product_list"))