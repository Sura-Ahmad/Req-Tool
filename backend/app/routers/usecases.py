import logging
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.requirements import Requirement
from app.models.domain import UserSession, Domain
from app.schemas.usecases import UseCasesRequest, UseCasesResponse, UseCaseItem
from app.core.config import settings
from app.core.limiter import limiter
import anthropic

logger = logging.getLogger("requirements_ai")
router = APIRouter(prefix="/usecases", tags=["Use Cases"])
client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


@router.post("/generate", response_model=UseCasesResponse)
@limiter.limit("10/minute")
def generate_use_cases(request: Request, data: UseCasesRequest, db: Session = Depends(get_db)):
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

    fr_text = "\n".join([f"{r.code}: {r.description}" for r in requirements])

    prompt = f"""Based on these functional requirements for a {domain.name} system in Jordan, generate use cases as structured text.

Functional Requirements:
{fr_text}

Generate use cases and return them as a JSON array. Each use case must have:
- title: short title
- actor: who performs this action
- preconditions: what must be true before
- main_flow: step by step flow as text
- postconditions: what happens after

Return ONLY a valid JSON array, no other text. Example:
[{{"title": "User Login", "actor": "Registered User", "preconditions": "User has an account", "main_flow": "1. User opens login page\\n2. User enters credentials\\n3. System validates\\n4. User is logged in", "postconditions": "User is authenticated"}}]"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()

    try:
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        use_cases_data = json.loads(response_text)
    except json.JSONDecodeError:
        logger.warning("Could not parse use-cases JSON response: %s", response_text[:200])
        use_cases_data = []

    use_cases = [UseCaseItem(**uc) for uc in use_cases_data]

    return UseCasesResponse(
        session_id=data.session_id,
        use_cases=use_cases,
        total=len(use_cases),
    )
