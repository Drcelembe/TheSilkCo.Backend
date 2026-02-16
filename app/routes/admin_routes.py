# app/routes/admin_routes.py
from flask import Blueprint
from app.utils.responses import success_response

bp = Blueprint("admin", __name__)

@bp.route("/health", methods=["GET"])
def health():
    return success_response({"status": "ok"}, "Admin health")
