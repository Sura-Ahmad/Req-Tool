from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.schemas.requirements import (
    GenerateRequirementsRequest, RequirementsResponse,
    ClassifiedRequirementsResponse, UpdateRequirementRequest, UpdateRequirementResponse,
)
from app.core.limiter import limiter
from app.services import requirement_service

router = APIRouter(prefix="/requirements", tags=["Requirements"])


@router.post("/generate", response_model=RequirementsResponse)
@limiter.limit("10/minute")
def generate(request: Request, data: GenerateRequirementsRequest, db: Session = Depends(get_db)):
    return requirement_service.generate_requirements(str(data.session_id), data.document_text, db)


@router.get("/{session_id}/classified", response_model=ClassifiedRequirementsResponse)
def get_classified_requirements(session_id: UUID, db: Session = Depends(get_db)):
    requirements = requirement_service.get_requirements_for_session(str(session_id), db)
    if not requirements:
        raise HTTPException(status_code=404, detail="No requirements found for this session")
    functional, non_functional = requirement_service.split_by_type(requirements)
    return ClassifiedRequirementsResponse(
        session_id=session_id,
        functional=functional,
        non_functional=non_functional,
        functional_count=len(functional),
        non_functional_count=len(non_functional),
        total=len(functional) + len(non_functional),
    )


@router.get("/{session_id}", response_model=RequirementsResponse)
def get_requirements(session_id: UUID, db: Session = Depends(get_db)):
    requirements = requirement_service.get_requirements_for_session(str(session_id), db)
    functional, non_functional = requirement_service.split_by_type(requirements)
    return RequirementsResponse(
        session_id=session_id,
        functional=functional,
        non_functional=non_functional,
        total=len(functional) + len(non_functional),
    )


@router.put("/{requirement_id}", response_model=UpdateRequirementResponse)
def update_requirement(requirement_id: str, data: UpdateRequirementRequest, db: Session = Depends(get_db)):
    return requirement_service.update_requirement(requirement_id, data.description, db)


@router.delete("/{requirement_id}")
def delete_requirement(requirement_id: str, db: Session = Depends(get_db)):
    return requirement_service.delete_requirement(requirement_id, db)


class AddRequirementRequest(BaseModel):
    session_id: str
    type: str
    description: str


@router.post("/add")
def add_requirement(data: AddRequirementRequest, db: Session = Depends(get_db)):
    return requirement_service.add_requirement(data.session_id, data.type, data.description, db)
