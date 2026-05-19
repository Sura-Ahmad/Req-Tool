import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.requirements import Requirement
from app.models.domain import UserSession, Domain
from app.schemas.usecases import UseCasesRequest, UseCasesResponse, UseCaseItem
from app.core.limiter import limiter
from app.services.ai_service import generate_use_cases

logger = logging.getLogger("requirements_ai")
router = APIRouter(prefix="/usecases", tags=["Use Cases"])


@router.post("/generate", response_model=UseCasesResponse)
@limiter.limit("10/minute")
def generate_use_cases_doc(request: Request, data: UseCasesRequest, db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.id == data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    domain = db.query(Domain).filter(Domain.id == session.domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    requirements = db.query(Requirement).filter(
        Requirement.session_id == data.session_id,
        Requirement.type == "functional",
    ).all()

    if not requirements:
        raise HTTPException(status_code=404, detail="No functional requirements found")

    use_cases_data = generate_use_cases(domain.name, session.country or "Jordan", requirements)
    use_cases = [UseCaseItem(**uc) for uc in use_cases_data]

    return UseCasesResponse(
        session_id=data.session_id,
        use_cases=use_cases,
        total=len(use_cases),
    )
