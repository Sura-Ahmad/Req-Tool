from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.security import verify_token
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.domain import Domain, Question, UserSession
from app.schemas.domain import DomainResponse, QuestionResponse, SessionCreate, SessionResponse
from typing import List
import json
import uuid

router = APIRouter(prefix="/domains", tags=["Domains"])

@router.get("/", response_model=List[DomainResponse])
def get_domains(country: str, db: Session = Depends(get_db)):
    domains = db.query(Domain).filter(
        Domain.country == country,
        Domain.is_active == True
    ).all()
    if not domains:
        raise HTTPException(status_code=404, detail="No domains found for this country")
    return domains

@router.get("/{domain_id}/questions", response_model=List[QuestionResponse])
def get_questions(domain_id: str, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(
        Question.domain_id == domain_id,
        Question.is_active == True
    ).order_by(Question.question_order).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this domain")
    return questions

@router.post("/session", response_model=SessionResponse, status_code=201)
def create_session(data: SessionCreate, request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    user_id = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        payload = verify_token(token)
        if payload:
            user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    domain = db.query(Domain).filter(Domain.id == data.domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    session = UserSession(
        user_id=uuid.UUID(user_id),
        domain_id=data.domain_id,
        country=data.country,
        role=data.role.value,
        answers=json.dumps([{"question_id": str(a.question_id), "answer": a.answer} for a in data.answers])
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session