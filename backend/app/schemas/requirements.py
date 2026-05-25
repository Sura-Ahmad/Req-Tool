from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class GenerateRequirementsRequest(BaseModel):
    session_id: UUID
    document_text: Optional[str] = ""

class RequirementItem(BaseModel):
    id: Optional[UUID] = None
    code: str
    description: str
    type: str

class RequirementsResponse(BaseModel):
    session_id: UUID
    functional: List[RequirementItem]
    non_functional: List[RequirementItem]
    total: int

class ClassifiedRequirementsResponse(BaseModel):
    session_id: UUID
    functional: List[RequirementItem]
    non_functional: List[RequirementItem]
    functional_count: int
    non_functional_count: int
    total: int

class UpdateRequirementRequest(BaseModel):
    description: str

class UpdateRequirementResponse(BaseModel):
    id: UUID
    code: str
    description: str
    type: str
    is_edited: bool

    class Config:
        from_attributes = True


class AddRequirementRequest(BaseModel):
    session_id: str
    type: str
    description: str