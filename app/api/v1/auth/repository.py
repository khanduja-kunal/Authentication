from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.user import User
from sqlalchemy import update

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def create_user_from_google(db: AsyncSession, email: str, name: str, picture: str = None):
    new_user = User(
        email=email,
        name=name,
        is_verified=True,  
        signed_up_via_google=True,
        profile_picture=picture,
        hashed_password="", 
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def update_user_profile_from_google(db: AsyncSession, user: User, name: str, picture: str = None):
    user.name = name
    if picture:
        user.profile_picture = picture
    await db.commit()
    await db.refresh(user)
    return user
