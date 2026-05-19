from sqlalchemy.orm import Session
from app.models.requirements import Requirement
from app.models.domain import Question


def get_requirements_for_session(session_id: str, db: Session, req_type: str = None) -> list:
    query = db.query(Requirement).filter(Requirement.session_id == session_id)
    if req_type:
        query = query.filter(Requirement.type == req_type)
    return query.all()


def get_questions_for_answers(raw_answers: list, db: Session) -> dict:
    """Bulk-fetch questions for a list of answers. Returns {question_id_str: question_text}.
    Replaces N+1 query loops that queried one question per answer."""
    question_ids = [a.get("question_id") for a in raw_answers if a.get("question_id")]
    if not question_ids:
        return {}
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    return {str(q.id): q.question_text for q in questions}
