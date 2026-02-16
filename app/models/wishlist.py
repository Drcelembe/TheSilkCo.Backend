# app/models/wishlist.py
from app.extensions import db
from datetime import datetime

class Wishlist(db.Model):
    __tablename__ = "wishlists"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    user = db.relationship("User", backref="wishlist_items", lazy=True)
    product = db.relationship("Product", backref="wishlisted_by", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "created_at": self.created_at,
            "product": self.product.to_dict_basic() if self.product else None
        }
