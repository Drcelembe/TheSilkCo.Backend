# app/models/__init__.py
# Import every model module so Alembic can detect db.Model subclasses
from app.extensions import db

# model modules
from app.models.user import User  # required in your project
from app.models.product import Product
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.reviews import Review
from app.models.webhook_log import WebhookLog
from app.models.wishlist import Wishlist

__all__ = [
    "db",
    "User", "Product", "Customer", "Order", "OrderItem",
    "Payment", "Review", "WebhookLog", "Wishlist"
]
