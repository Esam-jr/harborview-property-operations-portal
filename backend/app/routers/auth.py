from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthenticatedUser, TokenResponse, UserLogin, UserRead, UserRegister
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)) -> UserRead:
    existing_user = UserService.get_by_username(db, payload.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    user = UserService.create_user(
        db,
        payload.username,
        payload.password,
        payload.role,
        payload.shipping_address,
        payload.mailing_address,
    )
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = UserService.authenticate(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = create_access_token(user.username)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AuthenticatedUser)
def read_current_user(current_user: User = Depends(get_current_user)) -> AuthenticatedUser:
    return AuthenticatedUser(
        username=current_user.username,
        role=current_user.role,
        shipping_address=current_user.shipping_address,
        mailing_address=current_user.mailing_address,
    )
