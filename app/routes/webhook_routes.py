# app/routes/webhook_routes.py
from flask import Blueprint, request
from app.extensions import db
from app.models.webhook_log import WebhookLog
from app.utils.responses import success_response

bp = Blueprint("webhooks", __name__)

@bp.route("/payfast", methods=["POST"])
def payfast_webhook():
    payload = request.get_data(as_text=True)
    wl = WebhookLog(gateway="payfast", payload=payload, status="received")
    db.session.add(wl); db.session.commit()
    return success_response(None, "Webhook logged")
