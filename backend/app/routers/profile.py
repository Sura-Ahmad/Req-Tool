import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.core.security import verify_token, hash_password, verify_password

router = APIRouter(prefix="/profile", tags=["Profile"])

AVATAR_DIR = "uploads/avatars"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    return user


def _user_response(user: User) -> dict:
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role.value,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


# ── GET /profile/me ───────────────────────────────────────────────────────────

@router.get("/me")
def get_my_profile(current_user=Depends(get_current_user)):
    return _user_response(current_user)


# ── PUT /profile/update ───────────────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


@router.put("/update")
def update_profile(data: ProfileUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if data.email is not None:
        normalized = data.email.strip().lower()
        if normalized != current_user.email:
            taken = db.query(User).filter(User.email == normalized, User.id != current_user.id).first()
            if taken:
                raise HTTPException(status_code=400, detail="Email is already in use")
            current_user.email = normalized
    if data.full_name is not None:
        current_user.full_name = data.full_name.strip()
    db.commit()
    db.refresh(current_user)
    return _user_response(current_user)


# ── POST /profile/upload-avatar ───────────────────────────────────────────────

@router.post("/upload-avatar")
async def upload_avatar(file: UploadFile = File(...), current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only jpg, jpeg, png, webp files are allowed")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size must not exceed 5 MB")

    # Remove old avatar file if it exists
    if current_user.avatar_url:
        old_path = current_user.avatar_url.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)

    os.makedirs(AVATAR_DIR, exist_ok=True)
    safe_id = str(current_user.id).replace("-", "")
    filename = f"{safe_id}.{ext}"
    file_path = os.path.join(AVATAR_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    avatar_url = f"/uploads/avatars/{filename}"
    current_user.avatar_url = avatar_url
    db.commit()
    return {"avatar_url": avatar_url}


# ── DELETE /profile/avatar ────────────────────────────────────────────────────

@router.delete("/avatar")
def delete_avatar(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.avatar_url:
        file_path = current_user.avatar_url.lstrip("/")
        if os.path.exists(file_path):
            os.remove(file_path)
        current_user.avatar_url = None
        db.commit()
    return {"message": "Avatar removed"}


# ── PUT /profile/change-password ──────────────────────────────────────────────

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.put("/change-password")
def change_password(data: ChangePasswordRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    pwd = data.new_password
    if len(pwd) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    has_letter = any(c.isalpha() for c in pwd)
    has_digit = any(c.isdigit() for c in pwd)
    if not has_letter or not has_digit:
        raise HTTPException(status_code=400, detail="Password must contain at least 1 letter and 1 number")

    current_user.password_hash = hash_password(pwd)
    db.commit()
    return {"message": "Password updated successfully"}


