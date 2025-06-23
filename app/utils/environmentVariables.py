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