# app/routes/payments.py
from flask import Blueprint, request, jsonify, current_app, url_for
from decimal import Decimal
from app.extensions import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.payment import Payment
from app.utils.payfast import payfast_build_signature, payfast_process_url
import os

bp = Blueprint("payments", __name__, url_prefix="/payments")

# Create payment: frontend posts cart/order details -> backend creates order & returns PayFast payload
@bp.route("/create", methods=["POST"])
def create_payment():
    """
    Expected payload:
    {
      "user_id": <optional>,
      "customer_id": <optional>,
      "items": [ {"product_id": 1, "quantity":2}, ... ],
      "shipping_cost": 20.00,
      "payment_method": "payfast"
    }
    """
    data = request.get_json() or {}
    items = data.get("items", [])
    if not items:
        return jsonify({"success": False, "message": "No items provided"}), 400

    # compute subtotal
    subtotal = Decimal("0.00")
    order_items = []
    for it in items:
        pid = it.get("product_id")
        qty = int(it.get("quantity", 1))
        product = Product.query.get(pid)
        if not product:
            return jsonify({"success": False, "message": f"Product {pid} not found"}), 404
        price = Decimal(str(product.price))
        subtotal += price * qty
        order_items.append({"product": product, "qty": qty, "price": price})

    shipping_cost = Decimal(str(data.get("shipping_cost", "0.00")))
    total = subtotal + shipping_cost

    # Create Order record
    order = Order(
        user_id=data.get("user_id"),
        customer_id=data.get("customer_id"),
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        total=total,
        payment_method=data.get("payment_method", "payfast"),
        payment_status="pending",
        order_status="created"
    )
    db.session.add(order)
    db.session.flush()  # get order.id

    # Add items
    for it in order_items:
        oi = OrderItem(
            order_id=order.id,
            product_id=it["product"].id,
            quantity=it["qty"],
            price=it["price"]
        )
        db.session.add(oi)

    db.session.commit()

    # Build PayFast payload
    # m_payment_id is merchant reference (use order.id)
    pf_payload = {
        "merchant_id": current_app.config.get("PAYFAST_MERCHANT_ID"),
        "merchant_key": current_app.config.get("PAYFAST_MERCHANT_KEY"),
        "return_url": current_app.config.get("PAYFAST_RETURN_URL"),
        "cancel_url": current_app.config.get("PAYFAST_CANCEL_URL"),
        "notify_url": current_app.config.get("PAYFAST_NOTIFY_URL"),
        "m_payment_id": str(order.id),
        "amount": f"{total:.2f}",
        "item_name": f"SilkCo Order #{order.id}",
        "email_address": request.json.get("email") or ""
    }

    pf_pass = current_app.config.get("PAYFAST_PASSPHRASE", "") or None
    signature = payfast_build_signature(pf_payload, passphrase=pf_pass)

    # return payload and signature so frontend can submit a POST form to PayFast (recommended)
    return jsonify({
        "success": True,
        "order_id": order.id,
        "payfast": {
            "action_url": payfast_process_url(current_app.config.get("PAYFAST_SANDBOX", True)),
            "payload": pf_payload,
            "signature": signature
        }
    }), 201


# Return / Cancel endpoints (user experience)
@bp.route("/return")
def pf_return():
    return "Payment successful. You may close this window and check your order status."

@bp.route("/cancel")
def pf_cancel():
    return "Payment cancelled."

# IPN Notify handler
@bp.route("/notify", methods=["POST"])
def pf_notify():
    """
    PayFast IPN verification using passphrase. Updates the order record.
    """
    ipn = request.form.to_dict()
    current_app.logger.info("PAYFAST IPN RECEIVED: %s", ipn)

    # Extract provided signature, if present
    pf_signature = ipn.pop("signature", None)

    # Rebuild signature using passphrase (if set)
    pf_pass = current_app.config.get("PAYFAST_PASSPHRASE", "") or None
    generated_signature = payfast_build_signature(ipn, passphrase=pf_pass)

    if pf_signature and pf_signature != generated_signature:
        current_app.logger.warning("PayFast IPN signature mismatch")
        return "INVALID", 400

    # Check payment status
    payment_status = ipn.get("payment_status")
    m_payment_id = ipn.get("m_payment_id")  # merchant reference (our order id)
    pf_payment_id = ipn.get("pf_payment_id")
    amount_gross = ipn.get("amount_gross")

    if not m_payment_id:
        current_app.logger.warning("PayFast IPN missing m_payment_id")
        return "INVALID", 400

    order = Order.query.get(int(m_payment_id))
    if not order:
        current_app.logger.warning("PayFast IPN: order %s not found", m_payment_id)
        return "INVALID", 404

    # Save a Payment row (if you track payments)
    payment = Payment(
        order_id=order.id,
        amount=float(amount_gross) if amount_gross else None,
        gateway="payfast",
        transaction_id=pf_payment_id,
        status=payment_status,
        raw_response=str(ipn)
    )
    db.session.add(payment)

    # If complete -> mark as paid
    if payment_status == "COMPLETE":
        order.payment_status = "paid"
        order.order_status = "processing"
        order.payfast_payment_id = pf_payment_id
        order.payfast_merchant_reference = m_payment_id

    else:
        # handle other statuses as needed
        order.payment_status = payment_status or order.payment_status

    db.session.commit()
    return "OK", 200
