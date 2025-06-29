import ollama
from app.utils.environmentVariables import EMBEDDING_MODEL
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import File

def get_embedding(prompt: str) -> list:
    embedding_model=EMBEDDING_MODEL
    response = ollama.embeddings(model=embedding_model,prompt=prompt)
    return response.get('embedding', [])

def get_pdf_embedding(file_path: str) -> list:
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    if not documents:
        return []
    
    textSpliter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = textSpliter.split_documents(documents)

    embeddings = [get_embedding(chunk.page_content) for chunk in chunks]

    return embeddings, chunks