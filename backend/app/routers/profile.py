from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.user import User
from app.models.domain import UserSession, Domain
from app.models.requirements import Requirement
from app.core.security import hash_password, verify_password
from app.services.auth_service import get_current_user, validate_password_strength

router = APIRouter(prefix="/profile", tags=["Profile"])


def _user_response(user: User) -> dict:
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role.value,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


# ── GET /profile/me ───────────────────────────────────────────────────────────

@router.get("/me")
def get_my_profile(current_user=Depends(get_current_user)):
    return _user_response(current_user)


# ── GET /profile/sessions ─────────────────────────────────────────────────────

@router.get("/sessions")
def get_my_sessions(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = (
        db.query(UserSession)
        .filter(UserSession.user_id == current_user.id)
        .order_by(UserSession.created_at.desc())
        .all()
    )
    domain_ids = [s.domain_id for s in sessions]
    session_ids = [s.id for s in sessions]

    domains_map = {d.id: d for d in db.query(Domain).filter(Domain.id.in_(domain_ids)).all()}
    req_counts = dict(
        db.query(Requirement.session_id, func.count(Requirement.id))
        .filter(Requirement.session_id.in_(session_ids))
        .group_by(Requirement.session_id)
        .all()
    )

    return [
        {
            "session_id": str(s.id),
            "domain_name": domains_map[s.domain_id].name if s.domain_id in domains_map else "Unknown",
            "country": s.country,
            "role": s.role,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "requirements_count": req_counts.get(s.id, 0),
        }
        for s in sessions
    ]


# ── GET /profile/sessions/{session_id} ───────────────────────────────────────

@router.get("/sessions/{session_id}")
def get_session_by_id(session_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    session = (
        db.query(UserSession)
        .filter(UserSession.id == session_id, UserSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    domain = db.query(Domain).filter(Domain.id == session.domain_id).first()
    return {
        "session_id": str(session.id),
        "domain_name": domain.name if domain else "Unknown",
        "country": session.country,
        "role": session.role,
        "created_at": session.created_at.isoformat() if session.created_at else None,
    }


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


# ── PUT /profile/change-password ──────────────────────────────────────────────

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.put("/change-password")
def change_password(data: ChangePasswordRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    validate_password_strength(data.new_password)
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
