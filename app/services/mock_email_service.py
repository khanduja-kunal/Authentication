from app.core.config import settings

def send_mock_email(to_email: str, otp: str, purpose: str, name: str = "User"):
    subject = {
        "verify_email": "Verify Your Email Address",
        "reset_password": "Reset Your Password"
    }.get(purpose, "Your OTP Code")

    message = f"""
    From: {settings.MAIL_SENDER}
    To: {to_email}
    Subject: {subject}

    Hi {name},

    Here is your One-Time Password (OTP) to {purpose.replace('_', ' ')}: **{otp}**

    Please use this code within the next {settings.OTP_LIFETIME_MINUTES} minutes.

    If you didn’t request this, you can safely ignore this email.

    Best regards,  
    {settings.MAIL_SENDER}
    """

    print("[MOCK EMAIL]")
    print(message)
