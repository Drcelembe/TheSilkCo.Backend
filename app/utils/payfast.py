# app/utils/payfast.py
import hashlib
import os

def payfast_build_signature(payload: dict, passphrase: str = None) -> str:
    """
    Builds MD5 signature string for PayFast.
    payload : dict with string values (keys => values)
    If passphrase provided, include payload['passphrase'] = passphrase during signature build (per PayFast doc).
    """
    working = {k: str(v) for k, v in payload.items() if v is not None and v != ""}

    if passphrase:
        working['passphrase'] = passphrase

    # sort keys alphabetically
    items = sorted(working.items(), key=lambda kv: kv[0])
    # create "key=value" joined by &
    signature_string = "&".join(f"{k}={working[k]}" for k, _ in items)
    return hashlib.md5(signature_string.encode("utf-8")).hexdigest()


def payfast_process_url(sandbox=True):
    """
    Return base URL to send user for payment form POST/redirect (eng/process)
    """
    if sandbox:
        return "https://sandbox.payfast.co.za/eng/process"
    return "https://www.payfast.co.za/eng/process"
