from sqlalchemy import Column, String, Integer, Boolean, DateTime, text, func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False, server_default=text('false'))
    signed_up_via_google = Column(Boolean, default=False, server_default=text('false'), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    profile_picture = Column(String, nullable=True)