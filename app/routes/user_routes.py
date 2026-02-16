from flask import Blueprint, jsonify, request, g
from app.middleware.auth import jwt_required_with_user, admin_required
from models.user import User, db

user_bp = Blueprint("users", __name__)

@user_bp.route("/me", methods=["GET"])
@jwt_required_with_user
def get_me():
    u = g.current_user
    return jsonify({
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role
    })

@user_bp.route("/me", methods=["PUT"])
@jwt_required_with_user
def update_me():
    u = g.current_user
    data = request.json

    u.full_name = data.get("full_name", u.full_name)
    u.phone = data.get("phone", u.phone)

    db.session.commit()
    return jsonify({"status": "success"})


@user_bp.route("/", methods=["GET"])
@admin_required
def list_users():
    users = User.query.all()
    return jsonify([
        {"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role}
        for u in users
    ])
