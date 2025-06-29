from pymilvus import connections, utility, db, Collection
from app.schemas.jobOrderSchema import JobOrderMilvus
from app.utils.environmentVariables import MILVUS_DB_HOST, MILVUS_DB_PORT
from app.utils.exceptions import MilvusCollectionNotFoundError, MilvusTransactionFailure


con = connections.connect(host=MILVUS_DB_HOST, port=MILVUS_DB_PORT)

db.using_database('ResumeMatcher')

def insert_to_milvus(job_order, collection_name: str):
     
    if not utility.has_collection(collection_name):
        raise MilvusCollectionNotFoundError(name="MilvusCollectionNotFoundError", message=f"Collection {collection_name} does not exist in Milvus.")
    
    collection = Collection(name=collection_name)
    result = collection.insert([job_order.model_dump()])

    if result.insert_count == 0:
        raise MilvusTransactionFailure(name="MilvusTransactionFailure", message="Failed to insert job order into Milvus.")
    
    return job_order

def delete_from_milvus(job_order_id: int, collection_name: str, id_col: str = "id"):
    if not utility.has_collection(collection_name):
        raise MilvusCollectionNotFoundError(name="MilvusCollectionNotFoundError", message=f"Collection {collection_name} does not exist in Milvus.")


    collection = Collection(name=collection_name)
    result=collection.delete(f"{id_col} == {job_order_id}")

    if result.delete_count == 0:
        raise MilvusTransactionFailure(f"Failed to delete job order from Milvus.")
    
    return job_order_id

def update_in_milvus(job_order: JobOrderMilvus, collection_name: str):
    if not utility.has_collection(collection_name):
        raise MilvusCollectionNotFoundError(f"Collection {collection_name} does not exist in Milvus.")



    collection = Collection(name=collection_name)
    result = collection.upsert([job_order.model_dump()])

    if result.upsert_count == 0:
        raise MilvusTransactionFailure("Failed to update job order in Milvus.")

    return job_order

