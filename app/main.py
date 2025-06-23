import app.services.jobOrderServices as jobOrderServices
import app.schemas.jobOrderSchema as jobOrderSchema
from app.services.milvusDBConnection import insert_to_milvus, delete_from_milvus, update_in_milvus
from app.utils.vectorEmbedding import get_embedding  
from app.services.postgresDBConnection import get_db
from app.utils.exceptions import EnvVarNotFoundError, MilvusDocNotFoundError, PostgressNoRowFound, MilvusCollectionNotFoundError, MilvusTransactionFailure

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/job-orders/", response_model=list[jobOrderSchema.JobOrder])
def get_all_job_orders(db: Session = Depends(get_db)):
    data = jobOrderServices.get_job_orders(db)
    return data

@app.get("/job-orders/{job_order_id}", response_model=jobOrderSchema.JobOrder)
def get_job_order_by_id(job_order_id: int, db: Session = Depends(get_db)):
    job_order = jobOrderServices.get_job_order_by_id(db, job_order_id)
    return job_order

@app.put("/job-orders/{job_order_id}", response_model=jobOrderSchema.JobOrder)
def update_job_order(job_order_id: int, job_order: jobOrderSchema.JobOrderCreate, db: Session = Depends(get_db)):
    db_updated_job_order = jobOrderServices.update_job_order(db, job_order_id, job_order)
    if db_updated_job_order is None:
        raise HTTPException(status_code=404, detail="Job order not found")  
    
    vector = get_embedding(job_order.job_description)
    job_order_milvus = jobOrderSchema.JobOrderMilvus(id=job_order_id, vector=vector)
    update_in_milvus(job_order_milvus, "JobOrder")

    return db_updated_job_order

@app.post("/job-orders/", response_model=jobOrderSchema.JobOrder)
def create_job_order(job_order: jobOrderSchema.JobOrderCreate, db: Session = Depends(get_db)):
    db_job_order = jobOrderServices.create_job_order(db, job_order)
    if db_job_order is None:
        raise HTTPException(status_code=400, detail="Error creating job order")
    
    vector = get_embedding(job_order.job_description)
    job_order_milvus = jobOrderSchema.JobOrderMilvus(id=db_job_order.id, vector=vector)
    
    insert_to_milvus(job_order_milvus, "JobOrder")
    
    return db_job_order

@app.delete("/job-orders/{job_order_id}", response_model=jobOrderSchema.JobOrder)
def delete_job_order(job_order_id: int, db: Session = Depends(get_db)):
    db_deleted_job_order = jobOrderServices.delete_job_order(db, job_order_id)
    
    if db_deleted_job_order is None:
        raise HTTPException(status_code=404, detail="Job order not found")  
    
    delete_from_milvus(job_order_id, "JobOrder")

    return db_deleted_job_order

def create_exception_handler(status_code: int, initial_detail: str):
    async def exception_handler(request: Request, exc: Exception):
        message = exc.message or initial_detail
        return JSONResponse(
            status_code=status_code,
            content={"detail": message}
        )
    return exception_handler

app.add_exception_handler(
    exc_class_or_status_code=EnvVarNotFoundError,
    handler=create_exception_handler(status.HTTP_501_NOT_IMPLEMENTED, "Env variable is not configured properly")
)

app.add_exception_handler(
    exc_class_or_status_code=MilvusDocNotFoundError,
    handler=create_exception_handler(status.HTTP_400_BAD_REQUEST, "Invalid Request")
)

app.add_exception_handler(
    exc_class_or_status_code=PostgressNoRowFound,
    handler=create_exception_handler(status.HTTP_400_BAD_REQUEST, "Invalid Request")
)

app.add_exception_handler(
    exc_class_or_status_code=MilvusCollectionNotFoundError,
    handler=create_exception_handler(status.HTTP_503_SERVICE_UNAVAILABLE, "Milvus Collection Not Found")
)

app.add_exception_handler(
    exc_class_or_status_code=MilvusTransactionFailure,
    handler=create_exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR, "DB Transaction Failed")
)