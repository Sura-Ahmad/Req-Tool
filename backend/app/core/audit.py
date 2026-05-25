from sqlalchemy.orm import Session
from app.models.audit import AuditLog, LoginHistory
from typing import Optional


def log_action(
    db: Session,
    user_id,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    details: Optional[dict] = None,
    request=None,
):
    ip_address = None
    if request and request.client:
        ip_address = request.client.host

    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()


def log_login(
    db: Session,
    email: str,
    success: bool,
    user_id=None,
    request=None,
    failure_reason: Optional[str] = None,
):
    entry = LoginHistory(
        user_id=user_id,
        email_attempted=email,
        success=success,
        failure_reason=failure_reason,
    )
    db.add(entry)
    db.commit()
