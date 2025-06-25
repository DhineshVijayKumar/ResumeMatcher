from pydantic import BaseModel
from fastapi import Form
from typing import Optional

class CandidateCreateSchema(BaseModel):
    name: str 
    # email: str  # Uncomment if you add email
    @classmethod
    def _as_form(
        cls,
        name: str = Form(...),
        # email: str = Form(...),  # Uncomment if you add email
    ):
        return cls(name=name)  # Uncomment if you add email
    
    @classmethod
    def _as_form_optional(
        cls,
        name: Optional[str] = Form(None),
        # email: str = Form(None),  # Uncomment if you add email
    ):
        return cls(name=name)  # Uncomment if you add email

class CandidateSchema(CandidateCreateSchema):
    id: int
    class Config:
        from_attributes = True

class CandidateMilvus(BaseModel):
    candidate_id: int
    vector: list[float]
