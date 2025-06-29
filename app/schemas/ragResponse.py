from pydantic import BaseModel

class RAGResponse(BaseModel):
    candidate_id: int
    reason: str

class RAGResponseList(BaseModel):
    data: list[RAGResponse]

    class Config:
        from_attributes = True