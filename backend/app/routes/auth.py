from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as OrmSession

from app.database import get_db
from app.models import User
from app.routes.deps import get_current_user
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserOut
from app.services.profile_service import get_or_create_profile
from app.services.seed_service import DEMO_PASSWORD, seed_demo_data
from app.utils.security import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(user: User) -> AuthResponse:
    return AuthResponse(access_token=create_access_token(str(user.id)), user=UserOut.model_validate(user))


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, db: OrmSession = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email is already registered")
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    get_or_create_profile(db, user.id)
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: OrmSession = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return _auth_response(user)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/demo", response_model=AuthResponse)
def demo_login(db: OrmSession = Depends(get_db)):
    user = seed_demo_data(db)
    return _auth_response(user)


@router.get("/demo-credentials")
def demo_credentials():
    return {"email": "demo@memorytutor.com", "password": DEMO_PASSWORD}
