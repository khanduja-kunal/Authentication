# This file ensures all models are imported so Alembic can see them
from app.db.models.user import User
from app.db.models.otp import OTP
from app.db.models.blacklisted_token import BlacklistedToken

__all__ = ["User", "OTP", "BlacklistedToken"]
