import ollama
from app.utils.environmentVariables import get_env_variable
def get_embedding(prompt: str) -> list:
    embedding_model=get_env_variable('embedding_model')
    response = ollama.embeddings(model=embedding_model,prompt=prompt)
    return response.get('embedding', [])
