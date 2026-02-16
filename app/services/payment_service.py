import json
from datetime import datetime
from database import db
from models.payment import Payment
from models.order import Order
from models.webhook_log import WebhookLog

class PaymentService:
    # -----------------------------------------
    # PAYFAST WEBHOOK HANDLER
    # -----------------------------------------
    def process_payfast_webhook(self, data):
        payment_id = data.get("m_payment_id")  # PF reference
        pf_status = data.get("payment_status")

        # Log webhook
        self._log_webhook("payfast", json.dumps(data), pf_status)

        payment = Payment.query.get(payment_id)
        if not payment:
            return {"error": "Payment not found"}, 404

        # Already processed
        if payment.status == "completed":
            return {"message": "Payment already processed"}, 200

        # Update state
        if pf_status == "COMPLETE":
            payment.status = "completed"
            self._complete_order(payment.order_id)

        elif pf_status == "FAILED":
            payment.status = "failed"

        elif pf_status == "CANCELLED":
            payment.status = "cancelled"

        db.session.commit()
        return {"message": "IPN processed"}, 200

    # -----------------------------------------
    # OZOW WEBHOOK HANDLER
    # -----------------------------------------
    def process_ozow_webhook(self, payload, reference, status):
        # Log webhook
        self._log_webhook("ozow", json.dumps(payload), status)

        # Extract payment ID from reference: OZ-123
        if not reference or "-" not in reference:
            return {"error": "Invalid reference"}, 400

        payment_id = reference.split("-")[1]
        payment = Payment.query.get(payment_id)

        if not payment:
            return {"error": "Payment not found"}, 404

        # Already handled
        if payment.status == "completed":
            return {"message": "Already processed"}, 200

        if status.lower() == "complete":
            payment.status = "completed"
            self._complete_order(payment.order_id)

        elif status.lower() == "failed":
            payment.status = "failed"

        elif status.lower() == "cancelled":
            payment.status = "cancelled"

        db.session.commit()
        return {"message": "Webhook processed"}, 200

    # -----------------------------------------
    # INTERNAL — COMPLETE ORDER WHEN PAYMENT CLEARS
    # -----------------------------------------
    def _complete_order(self, order_id):
        order = Order.query.get(order_id)
        if not order:
            return

        order.status = "paid"
        order.created_at = datetime.utcnow()
        db.session.commit()

    # -----------------------------------------
    # INTERNAL — LOG WEBHOOK EVENTS
    # -----------------------------------------
    def _log_webhook(self, gateway, payload, status):
        log = WebhookLog(
            gateway=gateway,
            payload=payload,
            status=status
        )
        db.session.add(log)
        db.session.commit()
