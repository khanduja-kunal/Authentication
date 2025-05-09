"""# app/api/v1/user/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.api.v1.user.schema import UserProfileResponse, UserProfileUpdateMultipart
from app.db.models.user import User
from app.core.security import get_current_user
from uuid import uuid4
import shutil
import os

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

@router.get("/user/profile", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "profile_picture_url": current_user.profile_picture,
    }

@router.patch("/user/profile", response_model=UserProfileResponse)
async def update_my_profile(
    form_data: UserProfileUpdateMultipart = Depends(),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    if form_data.name:
        current_user.name = form_data.name

    if form_data.file:
        if form_data.file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPEG, PNG, and WEBP images are allowed."
            )

        ext = form_data.file.filename.split(".")[-1]
        filename = f"{uuid4().hex}.{ext}"
        filepath = os.path.join("profile_pictures", filename)

        # Save new file
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(form_data.file.file, buffer)

        # Delete old file
        if current_user.profile_picture:
            old_filename = current_user.profile_picture.split("/")[-1]  # Only filename
            old_filepath = os.path.join("profile_pictures", old_filename)
            if os.path.exists(old_filepath):
                try:
                    os.remove(old_filepath)
                except Exception as e:
                    print(f"Warning: Could not delete old profile picture: {e}")

        # Construct full URL and store in DB
        full_url = str(request.base_url) + f"profile_pictures/{filename}"
        current_user.profile_picture = full_url

    await db.commit()
    await db.refresh(current_user)

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "profile_picture_url": current_user.profile_picture,
    }
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.api.v1.user.schema import UserProfileResponse, UserProfileUpdateMultipart
from app.db.models.user import User
from app.core.security import get_current_user
from app.api.v1.user import service

router = APIRouter()

@router.get("/user/profile", response_model=UserProfileResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return service.build_user_profile_response(current_user)

@router.patch("/user/profile", response_model=UserProfileResponse)
async def update_my_profile(
    form_data: UserProfileUpdateMultipart = Depends(),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    updated_user = await service.update_user_profile(
        db=db,
        user=current_user,
        form_data=form_data,
        base_url=str(request.base_url),
    )
    return service.build_user_profile_response(updated_user)
