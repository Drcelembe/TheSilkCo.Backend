# services/payfast_service.py
import os
import requests

class PayfastService:
    def __init__(self):
        self.merchant_id = os.getenv("PAYFAST_MERCHANT_ID")
        self.merchant_key = os.getenv("PAYFAST_MERCHANT_KEY")
        self.passphrase = os.getenv("PAYFAST_PASSPHRASE", "")

    def build_request(self, data):
        # Build POST payload and signature — implement as per PayFast docs
        payload = data.copy()
        # TODO: implement signature hashing
        return payload
