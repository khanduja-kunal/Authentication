from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())