from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User, UserRole
from app.models.domain import Domain, Question, UserSession
from app.models.requirements import Requirement
from app.core.security import verify_token

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_current_admin(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/stats")
def get_stats(admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar()
    total_sessions = db.query(func.count(UserSession.id)).scalar()
    total_requirements = db.query(func.count(Requirement.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    return {
        "total_users": total_users,
        "total_sessions": total_sessions,
        "total_requirements": total_requirements,
        "active_users_count": active_users,
    }


@router.get("/users")
def get_users(admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []
    for user in users:
        sessions_count = db.query(func.count(UserSession.id)).filter(UserSession.user_id == user.id).scalar()
        result.append({
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "sessions_count": sessions_count,
        })
    return result


@router.put("/users/{user_id}/toggle-active")
def toggle_user_active(user_id: str, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    db.commit()
    return {"id": str(user.id), "is_active": user.is_active}


@router.get("/sessions")
def get_sessions(admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    sessions = db.query(UserSession).all()
    result = []
    for s in sessions:
        user = db.query(User).filter(User.id == s.user_id).first()
        domain = db.query(Domain).filter(Domain.id == s.domain_id).first()
        req_count = db.query(func.count(Requirement.id)).filter(Requirement.session_id == s.id).scalar()
        result.append({
            "id": str(s.id),
            "user_name": user.full_name if user else "Unknown",
            "user_email": user.email if user else "Unknown",
            "domain_name": domain.name if domain else "Unknown",
            "country": s.country,
            "role": s.role,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "requirements_count": req_count,
        })
    return result


@router.get("/domains")
def get_domains(admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    domains = db.query(Domain).all()
    return [
        {
            "id": str(d.id),
            "name": d.name,
            "name_ar": d.name_ar,
            "country": d.country,
            "is_active": d.is_active,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in domains
    ]


class DomainCreate(BaseModel):
    name: str
    name_ar: str
    country: str


@router.post("/domains")
def create_domain(data: DomainCreate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    domain = Domain(name=data.name, name_ar=data.name_ar, country=data.country)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return {
        "id": str(domain.id),
        "name": domain.name,
        "name_ar": domain.name_ar,
        "country": domain.country,
        "is_active": domain.is_active,
    }


class DomainUpdate(BaseModel):
    name: Optional[str] = None
    name_ar: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = None


@router.put("/domains/{domain_id}")
def update_domain(domain_id: str, data: DomainUpdate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    if data.name is not None:
        domain.name = data.name
    if data.name_ar is not None:
        domain.name_ar = data.name_ar
    if data.country is not None:
        domain.country = data.country
    if data.is_active is not None:
        domain.is_active = data.is_active
    db.commit()
    return {
        "id": str(domain.id),
        "name": domain.name,
        "name_ar": domain.name_ar,
        "country": domain.country,
        "is_active": domain.is_active,
    }


@router.delete("/domains/{domain_id}")
def delete_domain(domain_id: str, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    domain.is_active = False
    db.commit()
    return {"message": "Domain deactivated"}


@router.get("/domains/{domain_id}/questions")
def get_questions(domain_id: str, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.domain_id == domain_id).all()
    return [
        {
            "id": str(q.id),
            "domain_id": str(q.domain_id),
            "question_text": q.question_text,
            "question_text_ar": q.question_text_ar,
            "question_order": q.question_order,
            "is_active": q.is_active,
        }
        for q in questions
    ]


class QuestionCreate(BaseModel):
    question_text: str
    question_text_ar: str
    question_order: str


@router.post("/domains/{domain_id}/questions")
def create_question(domain_id: str, data: QuestionCreate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    question = Question(
        domain_id=domain_id,
        question_text=data.question_text,
        question_text_ar=data.question_text_ar,
        question_order=data.question_order,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return {
        "id": str(question.id),
        "domain_id": str(question.domain_id),
        "question_text": question.question_text,
        "question_text_ar": question.question_text_ar,
        "question_order": question.question_order,
        "is_active": question.is_active,
    }


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_text_ar: Optional[str] = None
    question_order: Optional[str] = None
    is_active: Optional[bool] = None


@router.put("/questions/{question_id}")
def update_question(question_id: str, data: QuestionUpdate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if data.question_text is not None:
        question.question_text = data.question_text
    if data.question_text_ar is not None:
        question.question_text_ar = data.question_text_ar
    if data.question_order is not None:
        question.question_order = data.question_order
    if data.is_active is not None:
        question.is_active = data.is_active
    db.commit()
    return {
        "id": str(question.id),
        "domain_id": str(question.domain_id),
        "question_text": question.question_text,
        "question_text_ar": question.question_text_ar,
        "question_order": question.question_order,
        "is_active": question.is_active,
    }


@router.delete("/questions/{question_id}")
def delete_question(question_id: str, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    question.is_active = False
    db.commit()
    return {"message": "Question deactivated"}
