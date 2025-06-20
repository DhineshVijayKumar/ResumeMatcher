from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import os

class MilvusService:
    def __init__(self, host: str = None, port: str = None, alias: str = "default"):
        """
        Initialize connection to the Milvus server.
        """
        self.alias = alias
        self.host = host or os.getenv('MILVUS_HOST', 'localhost')
        self.port = port or os.getenv('MILVUS_PORT', '19530')
        self._connect()

    def _connect(self):
        """
        Establish or re-establish the Milvus connection.
        """
        connections.connect(alias=self.alias, host=self.host, port=self.port)

    def _get_collection(self, name: str) -> Collection:
        """
        Retrieve an existing Collection instance.
        """
        if not utility.has_collection(name):
            raise ValueError(f"Collection '{name}' does not exist.")
        return Collection(name, using=self.alias)

    def _build_schema(self, dim: int, primary_key: str, metadata_fields: dict) -> CollectionSchema:
        """
        Create a CollectionSchema given vector dimension and metadata definitions.
        """
        fields = [
            FieldSchema(name=primary_key, dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim)
        ]
        for fname, (dtype, max_length) in metadata_fields.items():
            fields.append(FieldSchema(name=fname, dtype=dtype, max_length=max_length))
        return CollectionSchema(fields, description="Vector collection with metadata")

    def create_collection(self, name: str, dim: int, primary_key: str, metadata_fields: dict) -> Collection:
        """
        Create a new collection with vector embeddings and specified metadata fields.
        :raises ValueError: if metadata_fields is not provided or invalid
        """
        if utility.has_collection(name):
            return Collection(name, using=self.alias)

        if not metadata_fields or not isinstance(metadata_fields, dict):
            raise ValueError("'metadata_fields' must be a non-empty dict mapping field names to (DataType, max_length).")
        schema = self._build_schema(dim, primary_key, metadata_fields)
        return Collection(name, schema, using=self.alias)

    def drop_collection(self, collection_name: str) -> None:
        """
        Drop the entire collection from Milvus.
        """
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)

    def insert(self, collection_name: str, data: dict) -> list:
        """
        Insert entities into a collection.
        Returns generated primary keys.
        """
        collection = self._get_collection(collection_name)
        schema_fields = [f.name for f in collection.schema.fields]
        normalized = {}
        for field in schema_fields:
            if field not in data:
                continue
            value = data[field]
            if field == 'embedding':
                # Single vector -> list of one vector
                if isinstance(value, list) and (not value or not isinstance(value[0], (list, tuple))):
                    normalized[field] = [value]
                else:
                    normalized[field] = value
            else:
                normalized[field] = value if isinstance(value, (list, tuple)) else [value]
        lengths = {len(v) for v in normalized.values()}
        if len(lengths) > 1:
            raise ValueError("All fields must have the same number of values after normalization.")
        insert_data = [normalized[field] for field in schema_fields if field in normalized]
        result = collection.insert(insert_data)
        collection.flush()
        return result.primary_keys

    def get_all(self, collection_name: str, output_fields: list = None, limit: int = 1000) -> list:
        """
        Retrieve entities from the collection up to `limit`.
        """
        collection = self._get_collection(collection_name)
        pk = collection.schema.primary_field.name
        expr = f"{pk} >= 0"
        return collection.query(expr=expr, output_fields=output_fields, limit=limit)

    def get_by_id(self, collection_name: str, id_value: int, output_fields: list = None) -> list:
        """
        Retrieve entity by primary key ID.
        """
        collection = self._get_collection(collection_name)
        pk = collection.schema.primary_field.name
        expr = f"{pk} == {id_value}"
        return collection.query(expr=expr, output_fields=output_fields)

    def update_by_id(self, collection_name: str, id_value: int, data: dict) -> None:
        """
        Update an existing entity by deleting and reinserting with same ID.
        """
        self.delete_by_ids(collection_name, [id_value])
        data_with_id = {**data, collection_name: id_value}
        self.insert(collection_name, data_with_id)

    def delete_by_ids(self, collection_name: str, ids: list) -> None:
        """
        Delete entities by primary key IDs.
        """
        collection = self._get_collection(collection_name)
        pk = collection.schema.primary_field.name
        expr = f"{pk} in {ids}"
        collection.delete(expr)
        collection.flush()

    def search(self, collection_name: str, query_vectors: list, top_k: int = 10,
               params: dict = None, output_fields: list = None, expr: str = None):
        """
        Perform a vector search with optional filtering and metadata retrieval.
        """
        collection = self._get_collection(collection_name)
        search_params = params or {"metric_type": "L2", "params": {"nprobe": 10}}
        return collection.search(
            data=query_vectors,
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=output_fields
        )

    def get_stats(self, collection_name: str) -> dict:
        """
        Retrieve collection statistics.
        """
        if not utility.has_collection(collection_name):
            raise ValueError(f"Collection '{collection_name}' does not exist.")
        return utility.get_collection_stats(collection_name)

# Example usage
if __name__ == '__main__':
    svc = MilvusService()
    
    svc.create_collection(
        name='clients',
        dim=128,
        primary_key='id',
        metadata_fields={'client_name': (DataType.VARCHAR, 256), 'description': (DataType.VARCHAR, 1024)}
    )
    # Insert and get all
    ids = svc.insert('clients', {'client_name': ['Alice'], 'description': ['Desc'], 'embedding': [[0.1]*128]})
    print('All:', svc.get_all('clients', output_fields=['client_name','description'], limit=10))
    svc.drop_collection('clients')

    # svc.drop_collection('clients')  # Clean up
