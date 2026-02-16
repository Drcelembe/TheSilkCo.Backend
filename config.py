# config.py
import os
from dotenv import load_dotenv

# Load .env automatically
load_dotenv()

class Config:
    """Base config using environment variables from .env"""
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail config (optional for later)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    # PayFast config
    PAYFAST_MERCHANT_ID = os.getenv("PAYFAST_MERCHANT_ID", "32911247")
    PAYFAST_MERCHANT_KEY = os.getenv("PAYFAST_MERCHANT_KEY", "91c2xipvie96q")
    PAYFAST_PASSPHRASE = os.getenv("PAYFAST_PASSPHRASE", "ILuvTheSilkCo.21")
    PAYFAST_RETURN_URL = os.getenv("PAYFAST_RETURN_URL", "http://localhost:5000/return")
    PAYFAST_CANCEL_URL = os.getenv("PAYFAST_CANCEL_URL", "http://localhost:5000/cancel")
    PAYFAST_NOTIFY_URL = os.getenv("PAYFAST_NOTIFY_URL", "http://localhost:5000/notify")
    PAYFAST_SANDBOX = os.getenv("PAYFAST_SANDBOX", "1") == "1"  # True = sandbox, False = live

    # Ozow placeholders (for future integration)
    OZOW_SITE_CODE = os.getenv("OZOW_SITE_CODE")
    OZOW_PRIVATE_KEY = os.getenv("OZOW_PRIVATE_KEY")
    OZOW_API_KEY = os.getenv("OZOW_API_KEY")
    OZOW_SUCCESS_URL = os.getenv("OZOW_SUCCESS_URL")
    OZOW_CANCEL_URL = os.getenv("OZOW_CANCEL_URL")
    OZOW_ERROR_URL = os.getenv("OZOW_ERROR_URL")
    OZOW_NOTIFY_URL = os.getenv("OZOW_NOTIFY_URL")

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"

class ProductionConfig(Config):
    DEBUG = False
    ENV = "production"
