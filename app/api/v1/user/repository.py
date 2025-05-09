from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User

async def save_user_changes(db: AsyncSession, user: User) -> User:
    await db.commit()
    await db.refresh(user)
    return user
