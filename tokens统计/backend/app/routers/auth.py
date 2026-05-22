from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import auth
from app.models import User
from app.schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshRequest,
    UserResponse,
    CaptchaChallenge,
)

router = APIRouter()


@router.get("/auth/captcha", response_model=CaptchaChallenge)
def get_captcha():
    return CaptchaChallenge(token=auth.create_captcha_token())


@router.post("/auth/register", response_model=TokenResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(auth.get_db)):
    if not auth.verify_captcha_token(data.captcha_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Captcha verification failed",
        )

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=data.email,
        password_hash=auth.hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return TokenResponse(
        access_token=auth.create_access_token(user.id),
        refresh_token=auth.create_refresh_token(user.id),
    )


@router.post("/auth/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(auth.get_db)):
    if not auth.verify_captcha_token(data.captcha_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Captcha verification failed",
        )

    user = db.query(User).filter(User.email == data.email).first()
    if not user or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return TokenResponse(
        access_token=auth.create_access_token(user.id),
        refresh_token=auth.create_refresh_token(user.id),
    )


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest):
    payload = auth.verify_token(data.refresh_token, "refresh")
    user_id = int(payload["sub"])
    return TokenResponse(
        access_token=auth.create_access_token(user_id),
        refresh_token=auth.create_refresh_token(user_id),
    )


@router.get("/auth/me", response_model=UserResponse)
def me(current_user: User = Depends(auth.get_current_user)):
    return current_user
