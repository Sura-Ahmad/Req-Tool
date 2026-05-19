import logging
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.requirements import Requirement
from app.models.domain import UserSession, Domain
from app.schemas.crosscheck import CrossCheckResponse, IssueItem
from app.core.limiter import limiter
from app.core.knowledge_base import retrieve_context
from app.services.ai_service import run_crosscheck
from app.services.requirement_service import get_questions_for_answers

logger = logging.getLogger("requirements_ai")
router = APIRouter(prefix="/crosscheck", tags=["Cross-Check"])


@router.get("/{session_id}", response_model=CrossCheckResponse)
@limiter.limit("10/minute")
def cross_check(request: Request, session_id: str, db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    domain = db.query(Domain).filter(Domain.id == session.domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    raw_answers = json.loads(session.answers) if session.answers else []
    questions_map = get_questions_for_answers(raw_answers, db)
    answers_text = "\n".join([
        f"Q: {questions_map.get(a.get('question_id'), 'Unknown question')} A: {a.get('answer', '')}"
        for a in raw_answers
    ]) or "No user answers provided"

    requirements = db.query(Requirement).filter(Requirement.session_id == session_id).all()
    if not requirements:
        raise HTTPException(status_code=404, detail="No requirements found")

    req_list = "\n".join([f"{r.code}: {r.description}" for r in requirements])
    kb_context = retrieve_context(domain.name, req_list)
    issues_data = run_crosscheck(req_list, answers_text, kb_context)

    req_map = {r.code: r for r in requirements}
    color_map = {
        "ambiguity": "#FFA500",
        "duplicate": "#FF6B6B",
        "inconsistency": "#9B59B6",
        "conflict": "#FF0000",
        "unsupported": "#3498DB",
    }

    issues = []
    ambiguities = 0
    duplicates = 0
    inconsistencies = 0

    for issue in issues_data:
        code = issue.get("requirement_code", "")
        issue_type = issue.get("issue_type", "")
        req = req_map.get(code)

        if req and issue_type in color_map:
            issues.append(IssueItem(
                requirement_id=req.id,
                code=code,
                description=req.description,
                issue_type=issue_type,
                issue_detail=issue.get("issue_detail", ""),
                highlight_color=color_map[issue_type],
                conflict_with=issue.get("conflict_with", ""),
            ))
            if issue_type == "ambiguity":
                ambiguities += 1
            elif issue_type == "duplicate":
                duplicates += 1
            elif issue_type == "inconsistency":
                inconsistencies += 1

    return CrossCheckResponse(
        session_id=uuid.UUID(session_id),
        issues=issues,
        ambiguities_count=ambiguities,
        duplicates_count=duplicates,
        inconsistencies_count=inconsistencies,
        total_issues=len(issues),
    )
