# routes/test.py
from flask import Blueprint
from app.utils import json_success

bp = Blueprint("test", __name__, url_prefix="/test")

@bp.route("/ping")
def ping():
    return json_success({"pong": True}, "pong")
