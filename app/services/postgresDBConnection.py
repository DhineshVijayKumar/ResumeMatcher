from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.utils.environmentVariables import POSTGRES_DB_URL  

postgres_db_url = POSTGRES_DB_URL
engine = create_engine(postgres_db_url)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_table():
    Base.metadata.create_all(bind=engine)

def as_dict(obj):
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}