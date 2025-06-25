from pydantic import BaseModel

class JobApplicationCreateSchema(BaseModel):
    job_order_id: int
    candidate_id: int

class JobApplicationSchema(JobApplicationCreateSchema):
    candidate_score: int
    class Config:
        from_attributes = True

class JobApplicationDetailedSchema(JobApplicationSchema):
    candidate_name: str
    job_title: str
    client_name: str

