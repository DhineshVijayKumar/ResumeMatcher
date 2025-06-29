from typing import List, Callable, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from langchain_milvus import Milvus
from langchain_ollama import OllamaEmbeddings
import os

def build_rag_graph(
    db_name: str,
    collection_name: str,
    embedding_model: OllamaEmbeddings,
    llm,
    prompt_template: str = None,
    k: int = 5,
) -> Callable:
    """
    Returns a compiled RAG graph object.
    
    Parameters:
        vector_store: The vector store object for similarity search.
        llm: The language model object with an .invoke() method.
        prompt_template: (Optional) Custom prompt template string with {question} and {context}.
        k: (Optional) Number of documents to retrieve for context.
    """
    # Use default prompt if none provided
    if prompt_template is None:
        prompt_template = """
        Consider yourself as an API with rag capabilities. 
        Don't provide result with text. Provide result in list of JSON object with key candidate_id, reason.

        You will be provided with a question and a context.
        Your task is to generate a concise and accurate answer based on the context provided.
        If the context does not contain enough information to answer the question, respond with "I don't know".
        
        Context: {context}
        Question: {question}
        """
    prompt = ChatPromptTemplate.from_template(prompt_template)

    vector_store = Milvus(
        embedding_function=embedding_model,
        collection_name=collection_name,
        connection_args={
            "host": os.environ.get("milvus_db_host"),
            "port": os.environ.get("milvus_db_port"),
            "db_name": db_name
        },
        index_params={"index_type": "FLAT", "metric_type": "L2"},
    )
    class State(Dict):
        question: str
        context: List[Document]
        answer: str

    def retrieve(state: State):
        retrieved_docs = vector_store.similarity_search(state["question"], k=k)
        return {"context": retrieved_docs}

    def generate(state: State):
        docs_content = "\n\n".join(
            f'chunk: {doc.page_content}\nMetadata: {doc.metadata}' for doc in state["context"]
        )
        messages = prompt.invoke({"question": state["question"], "context": docs_content})
        response = llm.invoke(messages)
        return {"answer": response.content}

    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    return graph_builder.compile()

