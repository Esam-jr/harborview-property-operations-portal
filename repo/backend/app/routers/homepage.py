from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.homepage import HomePageConfigRead, HomePageConfigUpdate, HomePageContentRead
from app.services.homepage_service import HomePageService

router = APIRouter(prefix="/homepage", tags=["homepage"])


@router.get("", response_model=HomePageContentRead)
def get_homepage_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HomePageContentRead:
    return HomePageService.get_homepage_for_user(db, current_user)


@router.get("/config", response_model=HomePageConfigRead)
def get_homepage_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HomePageConfigRead:
    return HomePageService.get_admin_config(db, current_user)


@router.put("/config", response_model=HomePageConfigRead)
def update_homepage_config(
    payload: HomePageConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HomePageConfigRead:
    return HomePageService.update_admin_config(db, current_user, payload)
