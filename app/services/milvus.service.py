from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility, MilvusClient
import os

milvus_client = MilvusClient(uri="http://localhost:19530/")

collection_name = "my_rag_collection"

if milvus_client.has_collection(collection_name):
    print(f"Collection '{collection_name}' already exists.")
else:
    milvus_client.create_collection(collection_name)

