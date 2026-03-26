from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models so SQLAlchemy metadata is registered before create_all.
from app.models.user import User  # noqa: E402,F401
