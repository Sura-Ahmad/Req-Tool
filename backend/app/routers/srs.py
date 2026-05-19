import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.requirements import Requirement
from app.models.domain import UserSession, Domain
from app.schemas.srs import SRSRequest, SRSResponse
from app.core.limiter import limiter
from app.services.ai_service import generate_srs

logger = logging.getLogger("requirements_ai")
router = APIRouter(prefix="/srs", tags=["SRS"])


@router.post("/generate", response_model=SRSResponse)
@limiter.limit("5/minute")
def generate_srs_doc(request: Request, data: SRSRequest, db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.id == data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    domain = db.query(Domain).filter(Domain.id == session.domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    requirements = db.query(Requirement).filter(Requirement.session_id == data.session_id).all()
    if not requirements:
        raise HTTPException(status_code=404, detail="No requirements found")

    functional = [r for r in requirements if r.type == "functional"]
    non_functional = [r for r in requirements if r.type == "non_functional"]

    srs_content = generate_srs(
        data.project_name,
        data.project_description,
        domain.name,
        session.country or "Jordan",
        functional,
        non_functional,
    )

    return SRSResponse(
        session_id=data.session_id,
        project_name=data.project_name,
        content=srs_content,
        format="IEEE",
    )
