from pydantic import BaseModel

class JobOrderCreate(BaseModel):
    client_name: str
    job_title: str
    job_description: str

class JobOrder(JobOrderCreate):
    id: int
    class Config:
        from_attributes = True

class JobOrderMilvus(BaseModel):
    id: int
    vector: list[float]