from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_logger
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import (
    AuthenticatedUser,
    StaffProvisionRequest,
    TokenResponse,
    UserLogin,
    UserRead,
    UserRegister,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)) -> UserRead:
    existing_user = UserService.get_by_username(db, payload.username)
    if existing_user:
        logger.warning("Registration rejected: username already exists username=%s", payload.username)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    user = UserService.create_user(
        db,
        payload.username,
        payload.password,
        UserRole.resident,
        payload.shipping_address,
        payload.mailing_address,
    )
    logger.info("User registered username=%s role=%s", user.username, user.role.value)
    return UserRead.model_validate(user)


@router.post("/staff", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def provision_staff_user(
    payload: StaffProvisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    if current_user.role != UserRole.admin:
        logger.warning(
            "Staff provision forbidden actor_username=%s actor_role=%s requested_role=%s",
            current_user.username,
            current_user.role.value,
            payload.role.value,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin role can provision staff accounts",
        )

    existing_user = UserService.get_by_username(db, payload.username)
    if existing_user:
        logger.warning("Staff provision rejected: username already exists username=%s", payload.username)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    if payload.role == UserRole.resident:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Staff account role cannot be resident",
        )

    user = UserService.create_user(
        db,
        payload.username,
        payload.password,
        payload.role,
        payload.shipping_address,
        payload.mailing_address,
    )
    logger.info(
        "Staff account provisioned actor_username=%s new_username=%s role=%s",
        current_user.username,
        user.username,
        user.role.value,
    )
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = UserService.authenticate(db, payload.username, payload.password)
    if not user:
        logger.warning("Failed login attempt username=%s", payload.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = create_access_token(user.username)
    logger.info("Login success username=%s role=%s", user.username, user.role.value)
    if user.role.value in {"admin", "manager"}:
        logger.warning("Privileged login username=%s role=%s", user.username, user.role.value)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AuthenticatedUser)
def read_current_user(current_user: User = Depends(get_current_user)) -> AuthenticatedUser:
    logger.info("User profile requested username=%s role=%s", current_user.username, current_user.role.value)
    return AuthenticatedUser(
        username=current_user.username,
        role=current_user.role,
        shipping_address=current_user.shipping_address,
        mailing_address=current_user.mailing_address,
    )
