from services.payment_service import verify_webhook, record_payment
from models import WebhookLog, Order
from database import db
from datetime import datetime

def handle_payment_webhook(payload, gateway="payfast"):
    # 1) Verify signature/checksum
    ok = verify_webhook(payload)
    # 2) Log
    wl = WebhookLog(gateway=gateway, payload=str(payload), status="verified" if ok else "invalid", created_at=datetime.utcnow())
    db.session.add(wl)
    db.session.flush()
    # 3) If verified, update payment & order
    if ok:
        # Extract order id & amount & tx id depending on gateway format
        order_id = payload.get("order_id") or payload.get("merchant_order_id")
        amount = float(payload.get("amount", 0))
        tx = payload.get("transaction_id") or payload.get("pf_payment_id")
        record_payment(order_id=order_id, gateway=gateway, amount=amount, transaction_id=tx, status="success", raw_response=payload)
        # mark order payment_status
        order = Order.query.get(order_id)
        if order:
            order.payment_status = "paid"
            order.order_status = "processing"
            db.session.commit()
    else:
        db.session.commit()
    return ok
