from pydantic import BaseModel
from typing import List
from uuid import UUID

class UseCaseItem(BaseModel):
    title: str
    actor: str
    preconditions: str
    main_flow: str
    postconditions: str

class UseCasesRequest(BaseModel):
    session_id: UUID

class UseCasesResponse(BaseModel):
    session_id: UUID
    use_cases: List[UseCaseItem]
    total: int