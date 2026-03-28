from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import ProtectedMessage
from app.services.auth_mapper import to_authenticated_user

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/me", response_model=ProtectedMessage)
def protected_me(current_user: User = Depends(get_current_user)) -> ProtectedMessage:
    return ProtectedMessage(
        message="Access granted",
        user=to_authenticated_user(current_user),
        timestamp=datetime.now(timezone.utc),
    )
