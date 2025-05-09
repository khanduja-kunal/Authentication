# app/api/v1/user/endpoints.py
from fastapi import APIRouter, Depends, Request
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
