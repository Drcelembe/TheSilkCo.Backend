import hashlib
import urllib.parse
from flask import Blueprint, request, redirect
import config

payfast = Blueprint("payfast", __name__)

def create_signature(data):
    # Build signature string
    signature = ""
    for key in sorted(data.keys()):
        value = data[key]
        if value:
            signature += f"{key}={urllib.parse.quote_plus(str(value))}&"

    if config.PAYFAST_PASSPHRASE:
        signature += f"passphrase={config.PAYFAST_PASSPHRASE}"

    return hashlib.md5(signature.encode()).hexdigest()


@payfast.route("/pay", methods=["POST"])
def pay():
    amount = request.form.get("amount")
    item_name = request.form.get("item_name")

    data = {
        "merchant_id": config.PAYFAST_MERCHANT_ID,
        "merchant_key": config.PAYFAST_MERCHANT_KEY,
        "return_url": config.PAYFAST_RETURN_URL,
        "cancel_url": config.PAYFAST_CANCEL_URL,
        "notify_url": config.PAYFAST_NOTIFY_URL,
        "amount": amount,
        "item_name": item_name,
    }

    # Create secure signature
    data["signature"] = create_signature(data)

    # Select sandbox or live PayFast URL
    base_url = (
        "https://sandbox.payfast.co.za/eng/process"
        if config.PAYFAST_SANDBOX
        else "https://www.payfast.co.za/eng/process"
    )

    # Redirect user to PayFast
    query = urllib.parse.urlencode(data)
    return redirect(f"{base_url}?{query}")


@payfast.route("/return")
def return_handler():
    return "Payment Successful — Thank you."


@payfast.route("/cancel")
def cancel_handler():
    return "Payment Cancelled."


@payfast.route("/notify", methods=["POST"])
def notify_handler():
    # THIS FIRES EVEN IF THE USER CLOSES THE BROWSER
    print("PAYFAST IPN RECEIVED:", request.form)
    return "OK"
