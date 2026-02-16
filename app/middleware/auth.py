# app/middleware/auth.py
from functools import wraps
from flask import g, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from database import db
from app.models.user import User

def jwt_required_with_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({"success": False, "message": "Missing or invalid token"}), 401

        identity = get_jwt_identity()
        if not identity:
            return jsonify({"success": False, "message": "Invalid token identity"}), 401

        user = User.query.get(identity)
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        g.current_user = user
        return fn(*args, **kwargs)
    return wrapper
