class BaseError(Exception):
    """Base class for all exceptions in the application."""
    def __init__(self, message: str, name: str):
        self.message = message
        self.name = name
        super().__init__(self.message, self.name)

class EnvVarNotFoundError(BaseError):
    pass

class MilvusDocNotFoundError(BaseError):
    pass

class MilvusCollectionNotFoundError(BaseError):
    pass

class MilvusTransactionFailure(BaseError):
    pass

class PostgressNoRowFound(BaseError):
    pass

class PostgresTransactionFailure(BaseError):
    pass
