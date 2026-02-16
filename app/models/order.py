# app/models/order.py
from datetime import datetime
from app.extensions import db

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # nullable True if guest checkout
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True)

    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    shipping_cost = db.Column(db.Numeric(12, 2), nullable=True, default=0.00)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)

    payment_method = db.Column(db.String(50), nullable=True)
    payment_status = db.Column(db.String(50), nullable=False, default="pending")  # pending, paid, failed, refunded
    order_status = db.Column(db.String(50), nullable=False, default="created")    # created, processing, shipped, completed, cancelled

    payfast_payment_id = db.Column(db.String(255), nullable=True)  # pf_payment_id / pf_payment_id from IPN
    payfast_merchant_reference = db.Column(db.String(255), nullable=True)  # m_payment_id

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True)
    payments = db.relationship("Payment", backref="order", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "customer_id": self.customer_id,
            "subtotal": str(self.subtotal),
            "shipping_cost": str(self.shipping_cost),
            "total": str(self.total),
            "payment_status": self.payment_status,
            "order_status": self.order_status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
