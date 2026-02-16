# app/utils.py
from flask import jsonify

def json_success(data=None, message="OK", status=200):
    payload = {"status": "success", "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status

def json_error(message="Error", status=400, code=None):
    payload = {"status": "error", "message": message}
    if code:
        payload["code"] = code
    return jsonify(payload), status
