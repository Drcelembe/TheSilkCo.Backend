# app/routes/order_routes.py
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.utils.responses import success_response, error_response

bp = Blueprint("orders", __name__)

@bp.route("/", methods=["POST"])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    items = data.get("items", [])
    if not items:
        return error_response("items required", 400)
    order = Order(user_id=user_id, status="pending", total_amount=0)
    db.session.add(order)
    total = 0
    for it in items:
        pid = it.get("product_id"); qty = int(it.get("quantity", 1))
        product = Product.query.get(pid)
        if not product:
            db.session.rollback()
            return error_response(f"Product {pid} not found", 404)
        price = float(product.price)
        total += price * qty
        oi = OrderItem(order_id=order.id, product_id=pid, quantity=qty, price=price)
        db.session.add(oi)
    order.total_amount = total
    db.session.commit()
    return success_response({"order_id": order.id}, "Order created"), 201
