# services/ozow_service.py
import hashlib
import hmac
import json
import os

class OzowService:
    def __init__(self):
        self.site_code = os.getenv("OZOW_SITE_CODE")
        self.private_key = os.getenv("OZOW_PRIVATE_KEY")
        self.api_url = "https://api.ozow.com/postpaymentrequest"

    def generate_payment_request(self, amount, currency, reference, customer_email):
        payload = {
            "SiteCode": self.site_code,
            "CountryCode": "ZA",
            "CurrencyCode": currency,
            "Amount": float(amount),
            "TransactionReference": reference,
            "Customer": {"Email": customer_email},
            "CancelUrl": os.getenv("OZOW_CANCEL_URL"),
            "SuccessUrl": os.getenv("OZOW_SUCCESS_URL"),
            "ErrorUrl": os.getenv("OZOW_ERROR_URL"),
            "NotifyUrl": os.getenv("OZOW_NOTIFY_URL")
        }
        payload_str = json.dumps(payload, separators=(",", ":"))
        signature = hmac.new(
            self.private_key.encode(),
            payload_str.encode(),
            hashlib.sha512
        ).hexdigest()
        return {"payload": payload, "signature": signature}
