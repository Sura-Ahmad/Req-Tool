from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User, UserRole
from app.models.domain import Domain, Question, UserSession
from app.models.requirements import Requirement
from app.models.audit import AuditLog, LoginHistory
from app.core.security import verify_token
from app.core.audit import log_action

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
def toggle_user_active(user_id: str, request: Request, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    db.commit()
    log_action(
        db, admin.id,
        action="activate_user" if user.is_active else "deactivate_user",
        entity_type="user",
        entity_id=user_id,
        details={"email": user.email, "is_active": user.is_active},
        request=request,
    )
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
def create_domain(request: Request, data: DomainCreate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    domain = Domain(name=data.name, name_ar=data.name_ar, country=data.country)
    db.add(domain)
    db.commit()
    db.refresh(domain)
    log_action(
        db, admin.id,
        action="create_domain",
        entity_type="domain",
        entity_id=str(domain.id),
        details={"name": data.name, "name_ar": data.name_ar, "country": data.country},
        request=request,
    )
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
def update_domain(domain_id: str, request: Request, data: DomainUpdate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    changes = {}
    if data.name is not None:
        changes["name"] = {"old": domain.name, "new": data.name}
        domain.name = data.name
    if data.name_ar is not None:
        changes["name_ar"] = {"old": domain.name_ar, "new": data.name_ar}
        domain.name_ar = data.name_ar
    if data.country is not None:
        changes["country"] = {"old": domain.country, "new": data.country}
        domain.country = data.country
    if data.is_active is not None:
        changes["is_active"] = {"old": domain.is_active, "new": data.is_active}
        domain.is_active = data.is_active
    db.commit()
    log_action(
        db, admin.id,
        action="update_domain",
        entity_type="domain",
        entity_id=domain_id,
        details=changes,
        request=request,
    )
    return {
        "id": str(domain.id),
        "name": domain.name,
        "name_ar": domain.name_ar,
        "country": domain.country,
        "is_active": domain.is_active,
    }


@router.delete("/domains/{domain_id}")
def delete_domain(domain_id: str, request: Request, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    domain.is_active = False
    db.commit()
    log_action(
        db, admin.id,
        action="delete_domain",
        entity_type="domain",
        entity_id=domain_id,
        details={"name": domain.name},
        request=request,
    )
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
def create_question(domain_id: str, request: Request, data: QuestionCreate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    question = Question(
        domain_id=domain_id,
        question_text=data.question_text,
        question_text_ar=data.question_text_ar,
        question_order=data.question_order,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    log_action(
        db, admin.id,
        action="create_question",
        entity_type="question",
        entity_id=str(question.id),
        details={"domain_id": domain_id, "question_order": data.question_order},
        request=request,
    )
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
def update_question(question_id: str, request: Request, data: QuestionUpdate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    changes = {}
    if data.question_text is not None:
        changes["question_text"] = {"old": question.question_text, "new": data.question_text}
        question.question_text = data.question_text
    if data.question_text_ar is not None:
        changes["question_text_ar"] = {"old": question.question_text_ar, "new": data.question_text_ar}
        question.question_text_ar = data.question_text_ar
    if data.question_order is not None:
        changes["question_order"] = {"old": question.question_order, "new": data.question_order}
        question.question_order = data.question_order
    if data.is_active is not None:
        changes["is_active"] = {"old": question.is_active, "new": data.is_active}
        question.is_active = data.is_active
    db.commit()
    log_action(
        db, admin.id,
        action="update_question",
        entity_type="question",
        entity_id=question_id,
        details=changes,
        request=request,
    )
    return {
        "id": str(question.id),
        "domain_id": str(question.domain_id),
        "question_text": question.question_text,
        "question_text_ar": question.question_text_ar,
        "question_order": question.question_order,
        "is_active": question.is_active,
    }


@router.delete("/questions/{question_id}")
def delete_question(question_id: str, request: Request, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    question.is_active = False
    db.commit()
    log_action(
        db, admin.id,
        action="delete_question",
        entity_type="question",
        entity_id=question_id,
        details={"domain_id": str(question.domain_id)},
        request=request,
    )
    return {"message": "Question deactivated"}


# ── Audit Log ──────────────────────────────────────────────────────────────────

@router.get("/audit-log")
def get_audit_log(
    page: int = 1,
    limit: int = 20,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if date_from:
        query = query.filter(AuditLog.created_at >= datetime.fromisoformat(date_from))
    if date_to:
        query = query.filter(AuditLog.created_at <= datetime.fromisoformat(date_to))

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    items = []
    for entry in logs:
        user = db.query(User).filter(User.id == entry.user_id).first() if entry.user_id else None
        items.append({
            "id": str(entry.id),
            "user_id": str(entry.user_id) if entry.user_id else None,
            "user_name": user.full_name if user else None,
            "user_email": user.email if user else None,
            "action": entry.action,
            "entity_type": entry.entity_type,
            "entity_id": entry.entity_id,
            "details": entry.details,
            "ip_address": entry.ip_address,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": max(1, (total + limit - 1) // limit),
    }


# ── Login History ──────────────────────────────────────────────────────────────

@router.get("/login-history")
def get_login_history(
    page: int = 1,
    limit: int = 20,
    email: Optional[str] = None,
    success: Optional[bool] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(LoginHistory)
    if email:
        query = query.filter(LoginHistory.email_attempted.ilike(f"%{email}%"))
    if success is not None:
        query = query.filter(LoginHistory.success == success)
    if date_from:
        query = query.filter(LoginHistory.created_at >= datetime.fromisoformat(date_from))
    if date_to:
        query = query.filter(LoginHistory.created_at <= datetime.fromisoformat(date_to))

    total = query.count()
    entries = query.order_by(LoginHistory.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    items = [
        {
            "id": str(e.id),
            "user_id": str(e.user_id) if e.user_id else None,
            "email_attempted": e.email_attempted,
            "success": e.success,
            "ip_address": e.ip_address,
            "user_agent": e.user_agent,
            "failure_reason": e.failure_reason,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in entries
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": max(1, (total + limit - 1) // limit),
    }


@router.get("/login-history/failed-attempts")
def get_failed_attempts(admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(hours=24)
    results = (
        db.query(
            LoginHistory.email_attempted,
            func.count(LoginHistory.id).label("attempts"),
            func.max(LoginHistory.created_at).label("last_attempt"),
        )
        .filter(LoginHistory.success == False, LoginHistory.created_at >= since)
        .group_by(LoginHistory.email_attempted)
        .order_by(func.count(LoginHistory.id).desc())
        .limit(10)
        .all()
    )
    return [
        {
            "email": r.email_attempted,
            "attempts": r.attempts,
            "last_attempt": r.last_attempt.isoformat() if r.last_attempt else None,
        }
        for r in results
    ]
