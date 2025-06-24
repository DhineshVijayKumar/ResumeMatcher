from app.services.postgresDBConnection import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

class JobOrder(Base):
    __tablename__ = 'job_order'
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, index=True)
    job_title = Column(String, index=True)
    job_description = Column(String)

class Candidate(Base):
    __tablename__ = 'candidate'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

class JobApplication(Base):
    __tablename__ = 'job_application'
    job_order_id = Column(Integer, ForeignKey('job_order.id'), index=True, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidate.id'),index=True, primary_key=True)
    candidate_score = Column(Integer, index=True)