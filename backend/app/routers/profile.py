from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.services.auth_service import get_current_user
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me")
def get_my_profile(current_user=Depends(get_current_user)):
    return profile_service.format_user(current_user)


@router.get("/sessions")
def get_my_sessions(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return profile_service.get_user_sessions(current_user.id, db)


@router.get("/sessions/{session_id}")
def get_session_by_id(session_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return profile_service.get_session_by_id(session_id, current_user.id, db)


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


@router.put("/update")
def update_profile(data: ProfileUpdate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return profile_service.update_profile(current_user, data.email, data.full_name, db)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.put("/change-password")
def change_password(data: ChangePasswordRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    profile_service.change_password(current_user, data.current_password, data.new_password, db)
    return {"message": "Password updated successfully"}
