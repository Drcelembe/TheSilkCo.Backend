# app/routes/product_routes.py
from flask import Blueprint, request
from app.extensions import db
from app.models.product import Product
from app.utils.responses import success_response, error_response

bp = Blueprint("products", __name__)

@bp.route("/", methods=["GET"])
def list_products():
    q = Product.query.all()
    data = [{"id": p.id, "name": p.name, "price": str(p.price), "stock": p.stock} for p in q]
    return success_response(data, "Products list")

@bp.route("/", methods=["POST"])
def create_product():
    data = request.get_json() or {}
    name = data.get("name"); price = data.get("price")
    if not name or price is None:
        return error_response("name and price required", 400)
    p = Product(name=name, price=price, description=data.get("description"))
    db.session.add(p)
    db.session.commit()
    return success_response({"id": p.id}, "Product created"), 201
