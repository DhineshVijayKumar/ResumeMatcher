from pydantic import BaseModel
from fastapi import Form

class CandidateCreateSchema(BaseModel):
    name: str
    @classmethod
    def _as_form(
        cls,
        name: str = Form(...),
        # email: str = Form(...),  # Uncomment if you add email
    ):
        return cls(name=name)

class CandidateSchema(CandidateCreateSchema):
    id: int
    class Config:
        from_attributes = True

class CandidateMilvus(BaseModel):
    candidate_id: int
    vector: list[float]
