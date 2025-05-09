from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass
# Explicit model imports to register them with Base.metadata
# This ensures these models are "seen" by Alembic.


