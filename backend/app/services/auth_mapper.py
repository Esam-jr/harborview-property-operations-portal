from app.models.user import User
from app.schemas.auth import AuthenticatedUser


def to_authenticated_user(user: User) -> AuthenticatedUser:
    return AuthenticatedUser(username=user.username, role=user.role)
