# app/api/v1/auth/endpoints.py
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.db.models.user import User
from app.db.models.otp import OTP
from app.db.models.blacklisted_token import BlacklistedToken
from app.db.session import get_async_db
from app.api.v1.auth.schema import (
    RegisterRequest,
    OTPVerifyRequest,
    TokenResponse,
    ResendOTPRequest,
    PasswordResetRequest,
    PasswordResetVerify
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    validate_password_strength,
    get_current_user,
    oauth2_scheme
)
from app.core import google_oauth
from app.core.google_oauth import get_google_login_url
from app.api.v1.auth import service as auth_service
from app.utils.otp import send_otp
from app.services.mock_email_service import send_mock_email

router = APIRouter()

@router.post("/auth/register")
async def register_user(payload: RegisterRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).filter_by(email=payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    validate_password_strength(payload.password)

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )
    db.add(user)
    await db.commit()

    otp_entry = await send_otp(db, payload.email, purpose="verify_email")
    db.add(otp_entry)
    await db.commit()

    send_mock_email(payload.email, otp_entry.otp, purpose="verify_email", name=payload.name)
    return {"msg": "User registered. Please verify your email."}

@router.post("/auth/resend-verification-otp")
async def resend_verification_otp(payload: ResendOTPRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).filter_by(email=payload.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")

    otp_entry = await send_otp(db, payload.email, purpose="verify_email")
    send_mock_email(payload.email, otp_entry.otp, purpose="verify_email", name=user.name)
    return {"msg": "A new OTP has been sent to your email."}

@router.post("/auth/verify-email")
async def verify_email(payload: OTPVerifyRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(OTP).filter_by(email=payload.email, otp=payload.otp, purpose="verify_email")
    )
    otp_entry = result.scalar_one_or_none()

    if not otp_entry or otp_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    result = await db.execute(select(User).filter_by(email=payload.email))
    user = result.scalar_one_or_none()

    user.is_verified = True
    await db.delete(otp_entry)
    await db.commit()

    return {"msg": "Email verified successfully."}

@router.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(select(User).filter_by(email=form_data.username))
    user = result.scalar_one_or_none()

    if (
        not user
        or not user.is_verified
        or not user.hashed_password
        or not verify_password(form_data.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or email not verified"
        )

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token}

@router.post("/auth/request-password-reset")
async def request_password_reset(payload: PasswordResetRequest, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).filter_by(email=payload.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    otp_entry = await send_otp(db, payload.email, purpose="reset_password")
    db.add(otp_entry)
    await db.commit()

    send_mock_email(payload.email, otp_entry.otp, purpose="reset_password", name=user.name)
    return {"msg": "OTP sent to your email to reset password."}

@router.post("/auth/reset-password")
async def reset_password(payload: PasswordResetVerify, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(OTP).filter_by(email=payload.email, otp=payload.otp, purpose="reset_password")
    )
    otp_entry = result.scalar_one_or_none()

    if not otp_entry or otp_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    result = await db.execute(select(User).filter_by(email=payload.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    validate_password_strength(payload.new_password)
    user.hashed_password = hash_password(payload.new_password)

    await db.delete(otp_entry)
    await db.commit()

    return {"msg": "Password has been reset successfully."}

@router.post("/auth/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    blacklisted = BlacklistedToken(token=token)
    db.add(blacklisted)
    await db.commit()
    return {"msg": "Successfully logged out"}

@router.get("/api/v1/auth/google/callback", response_model=TokenResponse)
async def google_callback(request: Request, code: str, db: AsyncSession = Depends(get_async_db)):
    user_info = google_oauth.fetch_user_info_from_google(code)
    token = await auth_service.create_or_merge_user_via_google(user_info, db)
    return TokenResponse(access_token=token, token_type="bearer")

@router.get("/api/v1/auth/google-login")
async def google_login():
    auth_url, _ = get_google_login_url()
    return RedirectResponse(auth_url)
