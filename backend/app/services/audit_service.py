from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.audit import AuditLog, LoginHistory
from app.models.user import User


def get_audit_logs(
    db: Session,
    page: int = 1,
    limit: int = 20,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    query = db.query(AuditLog)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if date_from:
        query = query.filter(AuditLog.created_at >= datetime.fromisoformat(date_from))
    if date_to:
        dt_to = datetime.fromisoformat(date_to)
        if dt_to.hour == 0 and dt_to.minute == 0 and dt_to.second == 0:
            dt_to = dt_to.replace(hour=23, minute=59, second=59)
        query = query.filter(AuditLog.created_at <= dt_to)

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    log_user_ids = [e.user_id for e in logs if e.user_id]
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(log_user_ids)).all()} if log_user_ids else {}

    items = []
    for entry in logs:
        user = users_map.get(entry.user_id) if entry.user_id else None
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
            "created_at": (entry.created_at.isoformat() + "Z") if entry.created_at else None,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": max(1, (total + limit - 1) // limit),
    }


def get_login_history(
    db: Session,
    page: int = 1,
    limit: int = 20,
    email: Optional[str] = None,
    success: Optional[bool] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    query = db.query(LoginHistory)
    if email:
        query = query.filter(LoginHistory.email_attempted.ilike(f"%{email}%"))
    if success is not None:
        query = query.filter(LoginHistory.success == success)
    if date_from:
        query = query.filter(LoginHistory.created_at >= datetime.fromisoformat(date_from))
    if date_to:
        dt_to = datetime.fromisoformat(date_to)
        if dt_to.hour == 0 and dt_to.minute == 0 and dt_to.second == 0:
            dt_to = dt_to.replace(hour=23, minute=59, second=59)
        query = query.filter(LoginHistory.created_at <= dt_to)

    total = query.count()
    entries = query.order_by(LoginHistory.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    items = [
        {
            "id": str(e.id),
            "user_id": str(e.user_id) if e.user_id else None,
            "email_attempted": e.email_attempted,
            "success": e.success,
            "failure_reason": e.failure_reason,
            "created_at": (e.created_at.isoformat() + "Z") if e.created_at else None,
        }
        for e in entries
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": max(1, (total + limit - 1) // limit),
    }


def get_failed_login_attempts(db: Session, hours: int = 24, limit: int = 10) -> list:
    since = datetime.utcnow() - timedelta(hours=hours)
    results = (
        db.query(
            LoginHistory.email_attempted,
            func.count(LoginHistory.id).label("attempts"),
            func.max(LoginHistory.created_at).label("last_attempt"),
        )
        .filter(LoginHistory.success == False, LoginHistory.created_at >= since)
        .group_by(LoginHistory.email_attempted)
        .order_by(func.count(LoginHistory.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "email": r.email_attempted,
            "attempts": r.attempts,
            "last_attempt": (r.last_attempt.isoformat() + "Z") if r.last_attempt else None,
        }
        for r in results
    ]
