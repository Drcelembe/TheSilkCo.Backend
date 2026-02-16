# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import ProductionConfig as Config

import os
import hashlib
from dotenv import load_dotenv
from urllib.parse import urlencode

# Load .env variables
load_dotenv()

# Init extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize DB + migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # -------------------------------------------------
    # PAYFAST RETURN URLS (user-facing)
    # -------------------------------------------------
    @app.route("/return")
    def payfast_return():
        return "Payment Successful — Thank you!"

    @app.route("/cancel")
    def payfast_cancel():
        return "Payment Cancelled."

    # -------------------------------------------------
    # PAYFAST IPN (server-to-server verification)
    # -------------------------------------------------
    @app.route("/notify", methods=["POST"])
    def payfast_notify():
        """
        Verify PayFast IPN using passphrase + MD5 signature check.
        This endpoint is hit by PayFast, NOT the user.
        """

        ipn_data = request.form.to_dict()
        print("PAYFAST IPN RECEIVED:", ipn_data)

        # Step 1: Extract signature
        pf_signature = ipn_data.pop("signature", None)

        # Step 2: Build verification string
        pf_passphrase = os.getenv("PAYFAST_PASSPHRASE", "")
        if pf_passphrase:
            ipn_data["passphrase"] = pf_passphrase

        # PayFast requires alphabetical ordering
        sorted_keys = sorted(ipn_data.keys())
        signature_string = "&".join(f"{k}={ipn_data[k]}" for k in sorted_keys)

        # Step 3: Generate signature
        generated_signature = hashlib.md5(signature_string.encode("utf-8")).hexdigest()

        # Step 4: Compare signatures
        if pf_signature != generated_signature:
            print("❌ INVALID PAYFAST IPN SIGNATURE")
            return "INVALID", 400

        # Step 5: Validate payment status
        if ipn_data.get("payment_status") == "COMPLETE":
            order_id = ipn_data.get("m_payment_id")
            amount = ipn_data.get("amount_gross")
            print(f"✅ Payment verified | Order: {order_id} | Amount: {amount}")

            # TODO: update your DB
            # order = Order.query.get(order_id)
            # order.status = "paid"
            # db.session.commit()

        return "OK", 200

    return app


# Create app instance
app = create_app()

# Print env debug
print("SECRET_KEY:", os.getenv("SECRET_KEY"))
print("DB_URL:", os.getenv("DATABASE_URL"))
print("PAYFAST_KEY:", os.getenv("PAYFAST_MERCHANT_KEY"))
print("PAYFAST_PASSPHRASE:", os.getenv("PAYFAST_PASSPHRASE"))

# Run server
if __name__ == "__main__":
    app.run(debug=True)
