from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from enum import Enum

class ProjectRole(str, Enum):
    PO = "product_owner"
    BA = "business_analyst"
    DEVELOPER = "developer"
    STAKEHOLDER = "stakeholder"

class DomainResponse(BaseModel):
    id: UUID
    name: str
    name_ar: str
    country: str

    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    id: UUID
    domain_id: UUID
    question_text: str
    question_text_ar: str
    question_order: str

    class Config:
        from_attributes = True

class AnswerItem(BaseModel):
    question_id: UUID
    answer: str

class SessionCreate(BaseModel):
    domain_id: UUID
    country: str
    role: ProjectRole
    answers: List[AnswerItem]

class SessionResponse(BaseModel):
    id: UUID
    domain_id: UUID
    country: str
    role: str

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True