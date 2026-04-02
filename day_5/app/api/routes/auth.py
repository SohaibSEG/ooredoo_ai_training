from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import UserCreate, TokenPair, LoginRequest, RefreshRequest, AuthResponse, UserOut
from app.services.auth import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


@router.post("/register", response_model=AuthResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = service.register_user(db, payload.email, payload.name, payload.password)
    access, refresh = service.create_tokens(user)
    return AuthResponse(
        user=UserOut.model_validate(user),
        tokens=TokenPair(access_token=access, refresh_token=refresh),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = service.authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access, refresh = service.create_tokens(user)
    return AuthResponse(
        user=UserOut.model_validate(user),
        tokens=TokenPair(access_token=access, refresh_token=refresh),
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest):
    try:
        access = service.refresh_access_token(payload.refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc
    return TokenPair(access_token=access, refresh_token=payload.refresh_token)
