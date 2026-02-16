# app/__init__.py

import os
from flask import Flask
from flask_cors import CORS

from config import Config, DevelopmentConfig, ProductionConfig
from extensions import db, migrate, jwt, login_manager


def create_app():
    # -------------------------------------------------
    # Environment-based config selection
    # -------------------------------------------------
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        config_class = ProductionConfig
    elif env == "development":
        config_class = DevelopmentConfig
    else:
        config_class = Config  # fallback baseline

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class)

    # -------------------------------------------------
    # CORS
    # -------------------------------------------------
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # -------------------------------------------------
    # Initialize extensions
    # -------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)

    # -------------------------------------------------
    # Import ALL MODELS so Alembic can detect them
    # -------------------------------------------------
    with app.app_context():
        from app import models  # noqa: F401 (ensures models load)

    # -------------------------------------------------
    # Blueprint registration
    # -------------------------------------------------
    route_modules = [
        ("routes.auth_routes", "/auth"),
        ("routes.product_routes", "/products"),
        ("routes.order_routes", "/orders"),
        ("routes.review_routes", "/reviews"),
        ("routes.wishlist_routes", "/wishlist"),
        ("routes.webhook_routes", "/webhooks"),
        ("routes.admin_routes", "/admin"),
        ("routes.payments", "/payments"),
    ]

    for module_name, prefix in route_modules:
        try:
            mod = __import__(f"app.{module_name}", fromlist=["bp"])
            bp = getattr(mod, "bp", None)
            if bp:
                app.register_blueprint(bp, url_prefix=prefix)
        except Exception as e:
            print(f"⚠️ Blueprint load failed for {module_name}: {e}")

    # -------------------------------------------------
    return app
