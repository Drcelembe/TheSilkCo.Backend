# app/routes/review_routes.py
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.reviews import Review
from app.utils.responses import success_response, error_response

bp = Blueprint("reviews", __name__)

@bp.route("/", methods=["POST"])
@jwt_required()
def add_review():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    product_id = data.get("product_id"); rating = data.get("rating")
    if not product_id or rating is None:
        return error_response("product_id and rating required", 400)
    r = Review(product_id=product_id, user_id=user_id, rating=int(rating), comment=data.get("comment"))
    db.session.add(r)
    db.session.commit()
    return success_response({"id": r.id}, "Review added"), 201
