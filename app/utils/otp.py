# app/utils/otp.py
import random
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.otp import OTP
from app.core.config import settings

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def create_otp(email: str, purpose: str) -> OTP:
    now = datetime.utcnow()
    return OTP(
        email=email,
        otp=generate_otp(),
        purpose=purpose,
        created_at=now,
        expires_at=now + timedelta(minutes=settings.OTP_LIFETIME_MINUTES)
    )

async def send_otp(db: AsyncSession, email: str, purpose: str) -> OTP:
    now = datetime.utcnow()

    result = await db.execute(
        select(OTP)
        .filter_by(email=email, purpose=purpose)
        .order_by(OTP.created_at.desc())
    )
    last_otp = result.scalars().first()

    if last_otp:
        cooldown_end = last_otp.created_at + timedelta(seconds=settings.RESEND_COOLDOWN_SECONDS)
        if now < cooldown_end:
            remaining = int((cooldown_end - now).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {remaining} seconds before requesting another OTP."
            )

        await db.execute(
            OTP.__table__.delete().where(OTP.email == email, OTP.purpose == purpose)
        )

    new_otp = create_otp(email=email, purpose=purpose)
    db.add(new_otp)
    await db.commit()
    return new_otp