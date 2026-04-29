from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as OrmSession

from app.database import get_db
from app.models import User
from app.routes.deps import get_current_user
from app.schemas.profile import ProfileOut, ProfileUpdate, ProgressOut
from app.services.profile_service import get_or_create_profile, progress_snapshot


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
def get_profile(current_user: User = Depends(get_current_user), db: OrmSession = Depends(get_db)):
    return get_or_create_profile(db, current_user.id)


@router.put("", response_model=ProfileOut)
def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    profile = get_or_create_profile(db, current_user.id)
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        if value is not None:
            setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.put("/preferences", response_model=ProfileOut)
def update_preferences(
    preferences_json: dict,
    current_user: User = Depends(get_current_user),
    db: OrmSession = Depends(get_db),
):
    profile = get_or_create_profile(db, current_user.id)
    profile.preferences_json = preferences_json
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/progress", response_model=ProgressOut)
def get_progress(current_user: User = Depends(get_current_user), db: OrmSession = Depends(get_db)):
    return progress_snapshot(db, current_user.id)

