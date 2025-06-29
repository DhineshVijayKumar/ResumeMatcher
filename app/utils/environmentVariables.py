from dotenv import load_dotenv
import os
from pathlib import Path
from app.utils.exceptions import EnvVarNotFoundError

load_dotenv()

def get_env_variable(key):
    variable = os.getenv(key)
    if variable is None:
        raise EnvVarNotFoundError(message=f"Environment variable '{key}' not found.", name="EnvVarNotFoundError")
    return variable

MILVUS_DB_HOST = get_env_variable('MILVUS_DB_HOST')
MILVUS_DB_PORT = get_env_variable('MILVUS_DB_PORT')
POSTGRES_DB_URL = get_env_variable('POSTGRES_DB_URL')
EMBEDDING_MODEL = get_env_variable('EMBEDDING_MODEL')
DB_NAME = get_env_variable('DB_NAME')
GOOGLE_API_KEY = get_env_variable('GOOGLE_API_KEY')