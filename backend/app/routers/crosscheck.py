import logging
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.requirements import Requirement
from app.models.domain import UserSession, Question
from app.schemas.crosscheck import CrossCheckResponse, IssueItem
from app.core.config import settings
from app.core.limiter import limiter
from app.knowledge_base_loader import text_to_embedding, qdrant_client, COLLECTION_NAME
import anthropic

logger = logging.getLogger("requirements_ai")
router = APIRouter(prefix="/crosscheck", tags=["Cross-Check"])
client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


@router.get("/{session_id}", response_model=CrossCheckResponse)
@limiter.limit("10/minute")
def cross_check(request: Request, session_id: str, db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    raw_answers = json.loads(session.answers) if session.answers else []
    questions_map = {}
    for a in raw_answers:
        q = db.query(Question).filter(Question.id == a.get("question_id")).first()
        if q:
            questions_map[a.get("question_id")] = q.question_text
    answers_text = "\n".join([
        f"Q: {questions_map.get(a.get('question_id'), 'Unknown question')} A: {a.get('answer', '')}"
        for a in raw_answers
    ]) or "No user answers provided"

    requirements = db.query(Requirement).filter(Requirement.session_id == session_id).all()
    if not requirements:
        raise HTTPException(status_code=404, detail="No requirements found")

    req_list = "\n".join([f"{r.code}: {r.description}" for r in requirements])

    query_embedding = text_to_embedding(req_list)
    search_result = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=5,
    ).points
    kb_context = "\n".join([hit.payload["text"] for hit in search_result])

    prompt = f"""You are a senior requirements engineer.

Analyze the following requirements using:
1. Internal consistency (requirements vs requirements)
2. User answers (original input)
3. Domain knowledge (rules and regulations)

Requirements:
{req_list}

User Answers:
{answers_text}

Domain Knowledge:
{kb_context}

Find issues and return JSON array. Each issue must have:
- requirement_code: the code of the problematic requirement (e.g., "FR-1")
- issue_type: one of ["ambiguity", "duplicate", "inconsistency", "conflict", "unsupported"]
- issue_detail: clear explanation of the issue
- conflict_with: specify EXACTLY what this conflicts with:
  * If conflicts with another requirement: "Requirement FR-X" or "Requirement NFR-X"
  * If conflicts with domain rules: "Domain Knowledge: [quote the specific rule]"
  * If unsupported by user input: "User Answer: [quote what user said or didn't say]"
  * If duplicate: "Duplicate of FR-X"
  * If ambiguity: "N/A"

Return ONLY a valid JSON array. If no issues found, return []."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()

    try:
        clean_text = response_text
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_text:
            clean_text = clean_text.split("```")[1].split("```")[0].strip()
        issues_data = json.loads(clean_text)
    except json.JSONDecodeError:
        logger.warning("Could not parse cross-check JSON response: %s", response_text[:200])
        issues_data = []

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
