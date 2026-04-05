from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.requirements import Requirement
from app.models.domain import UserSession
from app.schemas.crosscheck import CrossCheckResponse, IssueItem
from app.core.config import settings
import anthropic
import json
import uuid

router = APIRouter(prefix="/crosscheck", tags=["Cross-Check"])

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

@router.get("/{session_id}", response_model=CrossCheckResponse)
def cross_check(session_id: str, db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    requirements = db.query(Requirement).filter(
        Requirement.session_id == session_id
    ).all()

    if not requirements:
        raise HTTPException(status_code=404, detail="No requirements found")

    req_list = "\n".join([f"{r.code}: {r.description}" for r in requirements])

    prompt = f"""You are a requirements engineer. Analyze these requirements and find issues.

Requirements:
{req_list}

Find and return a JSON array of issues. Each issue must have:
- requirement_code: the FR/NFR code
- issue_type: exactly one of "ambiguity", "duplicate", "inconsistency"
- issue_detail: brief explanation of the issue

Return ONLY a valid JSON array, no other text. Example:
[{{"requirement_code": "FR-1", "issue_type": "ambiguity", "issue_detail": "The term 'fast' is vague"}}]

If no issues found, return an empty array: []"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()
    
    try:
        issues_data = json.loads(response_text)
    except:
        issues_data = []

    req_map = {r.code: r for r in requirements}
    
    color_map = {
        "ambiguity": "#FFA500",
        "duplicate": "#FF6B6B",
        "inconsistency": "#9B59B6"
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
                highlight_color=color_map[issue_type]
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
        total_issues=len(issues)
    )