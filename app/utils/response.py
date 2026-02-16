# app/utils/responses.py
from flask import jsonify

def success_response(data=None, message="OK"):
    payload = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(payload)

def error_response(message="Something went wrong", status=400):
    payload = {
        "success": False,
        "message": message,
        "data": None
    }
    return jsonify(payload), status
