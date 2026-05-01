import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.requirements import Requirement
from app.models.domain import UserSession, Domain
from app.schemas.srs import SRSRequest, SRSResponse
from app.core.config import settings
from app.core.limiter import limiter
import anthropic

logger = logging.getLogger("requirements_ai")
router = APIRouter(prefix="/srs", tags=["SRS"])
client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


@router.post("/generate", response_model=SRSResponse)
@limiter.limit("5/minute")
def generate_srs(request: Request, data: SRSRequest, db: Session = Depends(get_db)):
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

    fr_text = "\n".join([f"{r.code}: {r.description}" for r in functional])
    nfr_text = "\n".join([f"{r.code}: {r.description}" for r in non_functional])

    prompt = f"""Generate a complete IEEE 830 Software Requirements Specification (SRS) document for the following project:

Project Name: {data.project_name}
Domain: {domain.name}
Country: Jordan
Description: {data.project_description}

Functional Requirements:
{fr_text}

Non-Functional Requirements:
{nfr_text}

Generate a complete SRS document following IEEE 830 standard with these sections:
1. Introduction
   1.1 Purpose
   1.2 Scope
   1.3 Definitions and Abbreviations
   1.4 References
   1.5 Overview
2. Overall Description
   2.1 Product Perspective
   2.2 Product Functions
   2.3 User Classes and Characteristics
   2.4 Operating Environment
   2.5 Constraints
3. Specific Requirements
   3.1 Functional Requirements
   3.2 Non-Functional Requirements
4. Appendices

Make it professional and complete."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    srs_content = message.content[0].text

    return SRSResponse(
        session_id=data.session_id,
        project_name=data.project_name,
        content=srs_content,
        format="IEEE",
    )
