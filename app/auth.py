# app/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.user import User
import datetime
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email"); password = data.get("password")
    if not email or not password:
        return jsonify({"error":"email and password required"}),400
    if User.query.filter_by(email=email).first():
        return jsonify({"error":"email exists"}),400
    u = User(full_name=data.get("full_name", ""), email=email)
    u.password_hash = generate_password_hash(password)
    db.session.add(u); db.session.commit()
    return jsonify({"success":True, "id": u.id}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email"); password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error":"invalid credentials"}),401
    access = create_access_token(identity=user.id)
    return jsonify({"token": access, "user": {"id": user.id, "email": user.email}})
