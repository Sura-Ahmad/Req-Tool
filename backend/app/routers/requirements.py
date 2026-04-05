from datetime import datetime
from app.schemas.requirements import GenerateRequirementsRequest, RequirementsResponse, RequirementItem, ClassifiedRequirementsResponse, UpdateRequirementRequest, UpdateRequirementResponse
from app.schemas.requirements import GenerateRequirementsRequest, RequirementsResponse, RequirementItem, ClassifiedRequirementsResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.requirements import Requirement
from app.models.domain import UserSession, Domain
from app.schemas.requirements import GenerateRequirementsRequest, RequirementsResponse, RequirementItem
from app.core.ai import generate_requirements
import uuid
import json

router = APIRouter(prefix="/requirements", tags=["Requirements"])

@router.post("/generate", response_model=RequirementsResponse)
def generate(data: GenerateRequirementsRequest, db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.id == data.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    domain = db.query(Domain).filter(Domain.id == session.domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    answers = json.loads(session.answers) if session.answers else []
    
    result = generate_requirements(
        domain=domain.name,
        role=session.role,
        answers=answers,
        document_text=data.document_text or ""
    )
    
    db.query(Requirement).filter(Requirement.session_id == session.id).delete()
    db.commit()
    
    functional_items = []
    non_functional_items = []
    
    for req in result["functional"]:
        parts = req.split(":", 1)
        if len(parts) == 2:
            req_obj = Requirement(
                session_id=session.id,
                code=parts[0].strip(),
                description=parts[1].strip(),
                type="functional"
            )
            db.add(req_obj)
            db.flush()
            functional_items.append(RequirementItem(
                id=req_obj.id,
                code=parts[0].strip(),
                description=parts[1].strip(),
                type="functional"
            ))
    
    for req in result["non_functional"]:
        parts = req.split(":", 1)
        if len(parts) == 2:
            req_obj = Requirement(
                session_id=session.id,
                code=parts[0].strip(),
                description=parts[1].strip(),
                type="non_functional"
            )
            db.add(req_obj)
            db.flush()
            non_functional_items.append(RequirementItem(
                id=req_obj.id,
                code=parts[0].strip(),
                description=parts[1].strip(),
                type="non_functional"
            ))
    
    db.commit()
    
    return RequirementsResponse(
        session_id=session.id,
        functional=functional_items,
        non_functional=non_functional_items,
        total=len(functional_items) + len(non_functional_items)
    )

@router.get("/{session_id}", response_model=RequirementsResponse)
def get_requirements(session_id: str, db: Session = Depends(get_db)):
    requirements = db.query(Requirement).filter(
        Requirement.session_id == session_id
    ).all()
    
    functional = [RequirementItem(id=r.id, code=r.code, description=r.description, type=r.type) 
                  for r in requirements if r.type == "functional"]
    non_functional = [RequirementItem(id=r.id, code=r.code, description=r.description, type=r.type) 
                      for r in requirements if r.type == "non_functional"]
    
    return RequirementsResponse(
        session_id=uuid.UUID(session_id),
        functional=functional,
        non_functional=non_functional,
        total=len(functional) + len(non_functional)
    )

@router.get("/{session_id}/classified", response_model=ClassifiedRequirementsResponse)
def get_classified_requirements(session_id: str, db: Session = Depends(get_db)):
    requirements = db.query(Requirement).filter(
        Requirement.session_id == session_id
    ).all()

    if not requirements:
        raise HTTPException(status_code=404, detail="No requirements found for this session")

    functional = [RequirementItem(id=r.id, code=r.code, description=r.description, type=r.type)
                  for r in requirements if r.type == "functional"]
    non_functional = [RequirementItem(id=r.id, code=r.code, description=r.description, type=r.type)
                      for r in requirements if r.type == "non_functional"]

    return ClassifiedRequirementsResponse(
        session_id=uuid.UUID(session_id),
        functional=functional,
        non_functional=non_functional,
        functional_count=len(functional),
        non_functional_count=len(non_functional),
        total=len(functional) + len(non_functional)
    )

@router.put("/{requirement_id}", response_model=UpdateRequirementResponse)
def update_requirement(requirement_id: str, data: UpdateRequirementRequest, db: Session = Depends(get_db)):
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    requirement.description = data.description
    requirement.is_edited = True
    requirement.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(requirement)
    return requirement