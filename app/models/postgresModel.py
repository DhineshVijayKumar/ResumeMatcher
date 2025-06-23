from app.services.postgresDBConnection import Base
from sqlalchemy import Column, Integer, String, DateTime

class JobOrder(Base):
    __tablename__ = 'job_order'
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, index=True)
    job_title = Column(String, index=True)
    job_description = Column(String)

