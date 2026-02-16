# app/routes/auth_routes.py
from flask import Blueprint, request
from app.extensions import db
from app.utils.responses import success_response, error_response
from app.models.user import User
from flask_jwt_extended import create_access_token

bp = Blueprint("auth", __name__)

@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email"); password = data.get("password"); name = data.get("name")
    if not email or not password:
        return error_response("email and password required", 400)
    if User.query.filter_by(email=email).first():
        return error_response("email exists", 409)
    user = User(full_name=name or "", email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return success_response({"id": user.id, "email": user.email}, "User created"), 201

@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email"); password = data.get("password")
    if not email or not password:
        return error_response("email and password required", 400)
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error_response("invalid credentials", 401)
    access_token = create_access_token(identity=user.id)
    return success_response({"access_token": access_token}, "Login successful")
