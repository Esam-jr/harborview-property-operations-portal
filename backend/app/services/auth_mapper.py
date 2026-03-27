from app.models.user import User
from app.schemas.auth import AuthenticatedUser


def to_authenticated_user(user: User) -> AuthenticatedUser:
    return AuthenticatedUser(
        username=user.username,
        role=user.role,
        shipping_address=user.shipping_address,
        mailing_address=user.mailing_address,
    )
