import os
import shutil
from uuid import uuid4
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.user.schema import UserProfileUpdateMultipart
from app.api.v1.user import repository
from app.db.models.user import User

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
PROFILE_PIC_DIR = "profile_pictures"

def build_user_profile_response(user: User):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "profile_picture_url": user.profile_picture,
    }

async def update_user_profile(db: AsyncSession, user: User, form_data: UserProfileUpdateMultipart, base_url: str):
    if form_data.name:
        user.name = form_data.name

    if form_data.file:
        file = form_data.file
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPEG, PNG, and WEBP images are allowed.",
            )

        ext = file.filename.split(".")[-1]
        filename = f"{uuid4().hex}.{ext}"
        filepath = os.path.join(PROFILE_PIC_DIR, filename)

        os.makedirs(PROFILE_PIC_DIR, exist_ok=True)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if user.profile_picture:
            old_file = user.profile_picture.split("/")[-1]
            old_path = os.path.join(PROFILE_PIC_DIR, old_file)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception as e:
                    print(f"Warning: Could not delete old profile picture: {e}")

        user.profile_picture = f"{base_url}profile_pictures/{filename}"

    updated_user = await repository.save_user_changes(db, user)
    return updated_user
