from flask import Blueprint

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return {"status": "Silk Co backend running"}
