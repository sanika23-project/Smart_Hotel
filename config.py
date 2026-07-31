import os

class Config:

    SECRET_KEY = "hotel123"

    DATABASE = "hotel.db"

    UPLOAD_FOLDER = "static/uploads"

# ==========================
# EMAIL CONFIGURATION
# ==========================

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False

# Your Gmail Address
MAIL_USERNAME = "yourgmail@gmail.com"

# Gmail App Password
MAIL_PASSWORD = "your_16_digit_app_password"

MAIL_DEFAULT_SENDER = "yourgmail@gmail.com"