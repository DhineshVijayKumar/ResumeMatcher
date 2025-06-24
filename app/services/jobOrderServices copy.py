
from app.models.postgresModel import JobOrder
from sqlalchemy.orm import Session
from app.schemas.jobOrderSchema import JobOrderCreate
from app.utils.exceptions import PostgressNoRowFound

def create_job_order(db: Session, job_order: JobOrderCreate):
    db_job_order = JobOrder(**job_order.model_dump())
    db.add(db_job_order)
    db.commit()
    db.refresh(db_job_order)
    return db_job_order

def get_job_orders(db: Session):
    return db.query(JobOrder).all()

def get_job_order_by_id(db: Session, job_order_id: int):
    result = db.query(JobOrder).filter(JobOrder.id == job_order_id).first()
    if result is None:
        raise PostgressNoRowFound(name="PostgressNoRowFound", message="No such Job Order Record")
    return result

def update_job_order(db: Session, job_order_id: int, job_order_data: JobOrderCreate):
    db_job_order = db.query(JobOrder).filter(JobOrder.id == job_order_id).first()
    if db_job_order is None:
        raise PostgressNoRowFound(name="PostgressNoRowFound", message="No such Job Order Record")
    for key, value in job_order_data.model_dump().items():
        setattr(db_job_order, key, value)

    db.commit()
    db.refresh(db_job_order)

    return db_job_order
    
def delete_job_order(db: Session, job_order_id: int):
    db_job_order = db.query(JobOrder).filter(JobOrder.id == job_order_id).first()

    if db_job_order is None:
        raise PostgressNoRowFound(name="PostgressNoRowFound", message="No such Job Order Record")

    db.delete(db_job_order)
    db.commit()
    return db_job_order
    
if __name__ == "__main__":
    from app.services.postgresDBConnection import sessionLocal, Base, engine
    from app.schemas.jobOrderSchema import JobOrderCreate

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = sessionLocal()

    # Create
    job_order_data = JobOrderCreate(
        client_name="Test Client",
        job_title="Test Title",
        job_description="Test Description"
    )
    new_job = create_job_order(db, job_order_data)
    print("Created:", vars(new_job))

    # Get all
    all_jobs = get_job_orders(db)
    print("All jobs:", [vars(job) for job in all_jobs])

    # Get by ID
    job = get_job_order_by_id(db, new_job.id)
    print("Fetched by ID:", vars(job))

    # Update
    job_order_data_update = JobOrderCreate(
        client_name="Updated Client",
        job_title="Updated Title",
        job_description="Updated Description"
    )
    updated_job = update_job_order(db, new_job.id, job_order_data_update)
    print("Updated:", vars(updated_job))

    # Delete
    deleted_job = delete_job_order(db, new_job.id)
    print("Deleted:", vars(deleted_job))

    db.close()