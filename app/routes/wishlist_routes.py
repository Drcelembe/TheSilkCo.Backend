# app/routes/wishlist_routes.py
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Wishlist, Product
from app.utils.responses import success_response, error_response

bp = Blueprint("wishlist", __name__)


# ------------------------------------------------------------
# GET /wishlist/me  → Get authenticated user's wishlist
# ------------------------------------------------------------
@bp.route("/me", methods=["GET"])
@jwt_required()
def get_my_wishlist():
    user_id = get_jwt_identity()

    items = (
        db.session.query(Wishlist, Product)
        .join(Product, Wishlist.product_id == Product.id)
        .filter(Wishlist.user_id == user_id)
        .all()
    )

    wishlist_data = [
        {
            "wishlist_id": w.Wishlist.id,
            "product_id": w.Product.id,
            "name": w.Product.name,
            "price": w.Product.price,
            "image": w.Product.image,
        }
        for w in items
    ]

    return success_response(data={"wishlist": wishlist_data}, message="Wishlist retrieved"), 200


# ------------------------------------------------------------
# POST /wishlist/add  → Add product to wishlist
# ------------------------------------------------------------
@bp.route("/add", methods=["POST"])
@jwt_required()
def add_to_wishlist():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    product_id = data.get("product_id")

    if not product_id:
        return error_response("product_id required", 400)

    # Check product exists
    product = Product.query.get(product_id)
    if not product:
        return error_response("Product not found", 404)

    # Check duplicates
    existing = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        return error_response("Already in wishlist", 409)

    item = Wishlist(user_id=user_id, product_id=product_id)
    db.session.add(item)
    db.session.commit()

    item_dict = {
        "wishlist_id": item.id,
        "product_id": product.id,
        "name": product.name,
        "price": product.price,
        "image": product.image,
    }

    return success_response(data=item_dict, message="Item added"), 201


# ------------------------------------------------------------
# DELETE /wishlist/remove/<product_id>  → Remove item
# ------------------------------------------------------------
@bp.route("/remove/<int:product_id>", methods=["DELETE"])
@jwt_required()
def remove_from_wishlist(product_id):
    user_id = get_jwt_identity()

    item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not item:
        return error_response("Item not in wishlist", 404)

    db.session.delete(item)
    db.session.commit()

    return success_response(message="Removed from wishlist"), 200
