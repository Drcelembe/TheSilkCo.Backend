from flask import Blueprint, request, jsonify, session, current_app, url_for
from .models import Product, WishlistItem, NewsletterSubscriber, Order
from . import db
import stripe
import os
from decimal import Decimal

main_bp = Blueprint('main', __name__)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

@main_bp.route("/api/products")
def products():
    prods = Product.query.limit(100).all()
    return jsonify([{
        'id': p.id, 'name': p.name, 'price': str(p.price), 'image_url': p.image_url
    } for p in prods])

# Wishlist endpoints (server-side)
@main_bp.route("/api/wishlist", methods=["GET"])
def get_wishlist():
    # Prefer user-specific, otherwise session
    user_id = session.get('user_id')  # optional if auth sets session user
    if user_id:
        items = WishlistItem.query.filter_by(user_id=user_id).all()
    else:
        s = session.get('sid')
        items = WishlistItem.query.filter_by(session_id=s).all() if s else []
    return jsonify([{'product_id': i.product_id, 'added_at': i.created_at.isoformat()} for i in items])

@main_bp.route("/api/wishlist", methods=["POST"])
def add_wishlist():
    data = request.json or {}
    pid = data.get('product_id')
    if not pid:
        return jsonify({'error':'product_id required'}), 400
    user_id = session.get('user_id')
    sid = session.get('sid') or session.sid if hasattr(session, 'sid') else session.get('_id')
    item = WishlistItem(user_id=user_id, session_id=sid, product_id=pid)
    db.session.add(item)
    db.session.commit()
    return jsonify({'success': True}), 201

@main_bp.route("/api/newsletter", methods=['POST'])
def newsletter():
    data = request.json or {}
    email = data.get('email')
    if not email:
        return jsonify({'error':'Email required'}), 400
    sub = NewsletterSubscriber.query.filter_by(email=email).first()
    if not sub:
        sub = NewsletterSubscriber(email=email)
        db.session.add(sub); db.session.commit()
    return jsonify({'success': True})

# Create Stripe checkout session
@main_bp.route("/api/checkout/create", methods=['POST'])
def create_checkout_session():
    data = request.json or {}
    # expect items: [{'product_id':1, 'qty': 1}, ...]
    items = data.get('items', [])
    if not items:
        return jsonify({'error':'No items'}), 400

    line_items = []
    total = Decimal('0.00')
    for it in items:
        p = Product.query.get(it['product_id'])
        qty = int(it.get('qty', 1))
        if not p: continue
        line_items.append({
            'price_data': {
                'currency': 'zar',
                'product_data': {'name': p.name},
                'unit_amount': int(float(p.price) * 100),
            },
            'quantity': qty,
        })
        total += Decimal(p.price) * qty

    success_url = request.host_url + "checkout/success?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.host_url + "cart"

    session_obj = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )

    # create order record (pending)
    order = Order(user_id=session.get('user_id'), stripe_session_id=session_obj.id, total_amount=total, status='pending')
    db.session.add(order); db.session.commit()

    return jsonify({'checkout_url': session_obj.url, 'session_id': session_obj.id})
