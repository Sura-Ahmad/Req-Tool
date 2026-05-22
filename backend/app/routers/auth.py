from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, RefreshToken, PasswordResetToken
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.core.security import hash_password, verify_password, verify_token
from app.core.email import send_reset_email
from app.core.audit import log_login
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.auth_service import hash_token, create_tokens, store_refresh_token, validate_password_strength, get_current_user
from app.core.limiter import limiter
import secrets

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("5/minute")
def register(request: Request, data: RegisterRequest, db: Session = Depends(get_db)):
    ALLOWED_DOMAINS = {"cit.just.edu.jo", "just.edu.jo", "outlook.com", "yahoo.com", "gmail.com"}
    email_domain = data.email.split("@")[-1].lower()
    if email_domain not in ALLOWED_DOMAINS:
        raise HTTPException(status_code=400, detail="Registration is only allowed for authorized email domains")
    validate_password_strength(data.password)
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token, refresh_token = create_tokens(user.id)
    store_refresh_token(user.id, refresh_token, db)
    db.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        log_login(db, email=data.email, success=False, request=request, failure_reason="user_not_found")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(data.password, user.password_hash):
        log_login(db, email=data.email, success=False, user_id=user.id, request=request, failure_reason="wrong_password")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        log_login(db, email=data.email, success=False, user_id=user.id, request=request, failure_reason="account_disabled")
        raise HTTPException(status_code=401, detail="Account is disabled")
    log_login(db, email=data.email, success=True, user_id=user.id, request=request)
    user.last_login = datetime.utcnow()
    db.commit()
    access_token, refresh_token = create_tokens(user.id)
    store_refresh_token(user.id, refresh_token, db)
    db.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/logout")
def logout(data: RefreshRequest, db: Session = Depends(get_db)):
    db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == hash_token(data.refresh_token)).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()
    return {"message": "Logged out successfully"}

@router.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(request: Request, data: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user and user.is_active:
        # Invalidate any existing unused tokens for this user
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.is_used == False
        ).update({"is_used": True})
        db.flush()

        token = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_token(token),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(reset_token)
        db.commit()

        reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        background_tasks.add_task(send_reset_email, user.email, user.full_name, reset_link)

    # Always return the same response to prevent email enumeration
    return {"message": "If this email is registered, you will receive a password reset link."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    validate_password_strength(data.new_password)

    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == hash_token(data.token),
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()

    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link. Please request a new one.")

    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.password_hash = hash_password(data.new_password)
    reset_token.is_used = True
    db.commit()

    return {"message": "Password reset successfully. You can now log in with your new password."}


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return user


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    payload = verify_token(data.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == hash_token(data.refresh_token),
        RefreshToken.is_revoked == False
    ).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Token revoked or not found")

    db_token.is_revoked = True
    new_access_token, new_refresh_token = create_tokens(db_token.user_id)
    store_refresh_token(db_token.user_id, new_refresh_token, db)
    db.commit()
    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)