from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import repository
from app.core.security import create_access_token

async def create_or_merge_user_via_google(user_info: dict, db: AsyncSession) -> str:
    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")

    user = await repository.get_user_by_email(db, email)
    if user:
        user = await repository.update_user_profile_from_google(db, user, name, picture)
    else:
        user = await repository.create_user_from_google(db, email, name, picture)

    # Generate JWT
    token = create_access_token(data={"sub": str(user.email)})
    return token
