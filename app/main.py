from app.services.postgresServices import GenericDBService
import app.schemas.jobOrderSchema as jobOrderSchema
from app.schemas.candidateSchema import CandidateSchema, CandidateCreateSchema, CandidateMilvus
from app.services.milvusDBConnection import insert_to_milvus, delete_from_milvus, update_in_milvus
from app.utils.vectorEmbedding import get_embedding, get_pdf_embedding
from app.services.postgresDBConnection import get_db, as_dict
from app.utils.exceptions import EnvVarNotFoundError, MilvusDocNotFoundError, PostgressNoRowFound, MilvusCollectionNotFoundError, MilvusTransactionFailure, FileUploadError
from app.models.postgresModel import JobOrder, Candidate, JobApplication

from fastapi import FastAPI, Depends, HTTPException, Request, status, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os

app = FastAPI()


@app.get("/job-orders/", response_model=list[jobOrderSchema.JobOrder], tags=["Job Orders"])
def get_all_job_orders(db: Session = Depends(get_db)):
    jobOrderServices = GenericDBService(db, JobOrder)
    data = jobOrderServices.get_all()
    return data

@app.get("/job-orders/{job_order_id}", response_model=jobOrderSchema.JobOrder, tags=["Job Orders"])
def get_job_order_by_id(job_order_id: int, db: Session = Depends(get_db)):
    jobOrderServices = GenericDBService(db, JobOrder)
    job_order = jobOrderServices.get_by_id(job_order_id)
    return job_order

@app.put("/job-orders/{job_order_id}", response_model=jobOrderSchema.JobOrder, tags=["Job Orders"])
def update_job_order(job_order_id: int, job_order: jobOrderSchema.JobOrderCreate, db: Session = Depends(get_db)):
    jobOrderServices = GenericDBService(db, JobOrder)
    db_updated_job_order = jobOrderServices.update(job_order_id, job_order)
    if db_updated_job_order is None:
        raise HTTPException(status_code=404, detail="Job order not found")  
    
    vector = get_embedding(job_order.job_description)
    job_order_milvus = jobOrderSchema.JobOrderMilvus(id=job_order_id, vector=vector)
    update_in_milvus(job_order_milvus, "JobOrder")

    jobOrderServices.commit()
    jobOrderServices.refresh(db_updated_job_order)

    return db_updated_job_order

@app.post("/job-orders/", response_model=jobOrderSchema.JobOrder, tags=["Job Orders"])
def create_job_order(job_order: jobOrderSchema.JobOrderCreate, db: Session = Depends(get_db)):
    jobOrderServices = GenericDBService(db, JobOrder)

    
    db_job_order = jobOrderServices.create(job_order)
    if db_job_order is None:
        raise HTTPException(status_code=400, detail="Error creating job order")
    
    db_job_order = as_dict(db_job_order)
    created_id = db_job_order['id']
    vector = get_embedding(job_order.job_description)
    job_order_milvus = jobOrderSchema.JobOrderMilvus(id=created_id, vector=vector)
    
    insert_to_milvus(job_order_milvus, "JobOrder")
    
    jobOrderServices.commit()

    return db_job_order

@app.delete("/job-orders/{job_order_id}", response_model=jobOrderSchema.JobOrder, tags=["Job Orders"])
def delete_job_order(job_order_id: int, db: Session = Depends(get_db)):
    jobOrderServices = GenericDBService(db, JobOrder)

    db_deleted_job_order = jobOrderServices.delete(job_order_id)
    
    if db_deleted_job_order is None:
        raise HTTPException(status_code=404, detail="Job order not found")  
    
    delete_from_milvus(job_order_id, "JobOrder")
    jobOrderServices.commit()

    return db_deleted_job_order


@app.post("/candidates/", response_model=CandidateSchema, tags=["Candidates"])
async def create_candidate(
    candidate: CandidateCreateSchema = Depends(CandidateCreateSchema._as_form), 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
    ):
    try:
        candidate_services = GenericDBService(db, Candidate)
        db_candidate = candidate_services.create(candidate)
        
        db.flush()
        db_candidate = as_dict(db_candidate)

        file_content = await file.read()
        if not file_content:
            raise FileUploadError(name="FileUploadError", message="File is empty or not provided")

        #save file to disk use __dirname__ to get the current directory
        
        file_path = f"app/uploads/{db_candidate['id']}.pdf"
        with open(file_path, "wb") as f:
            f.write(file_content)

        #get embedding from pdf
        embeddings = get_pdf_embedding(file_path)

        for embedding in embeddings:
            candidate_milvus = CandidateMilvus(candidate_id=db_candidate['id'], vector=embedding)
            insert_to_milvus(candidate_milvus, "Candidate")

        candidate_services.commit()

    except Exception as e:
        #remove the file if any error occurs
        db.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)
        raise 
        
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=db_candidate)
    


def create_exception_handler(status_code: int, initial_detail: str):
    async def exception_handler(request: Request, exc: Exception):
        if hasattr(exc, "message"):
            message = exc.message or initial_detail
        else:
            message = f"{initial_detail} | {str(exc)}"
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

## ollama connection error 
app.add_exception_handler(
    exc_class_or_status_code=ConnectionError,
    handler=create_exception_handler(status.HTTP_503_SERVICE_UNAVAILABLE, "Unable to connect with Ollama")
)

app.add_exception_handler(
    exc_class_or_status_code=Exception,
    handler=create_exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR, "UnExpected Error")
)