import logging
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from .loader import load_knowledge_base

logger = logging.getLogger(__name__)

# Singleton – built once on first call, reused for every subsequent retrieval
_vectorstore: FAISS | None = None


def _build_vectorstore() -> FAISS:
    """
    Embed all knowledge-base chunks and store them in a local FAISS index.
    Uses the lightweight all-MiniLM-L6-v2 sentence-transformer model so the
    project runs without any external embedding API key.
    """
    logger.info("Building FAISS vector store from knowledge base …")
    chunks = load_knowledge_base()
    docs = [Document(page_content=chunk) for chunk in chunks]

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    store = FAISS.from_documents(docs, embeddings)
    logger.info(f"Vector store ready — {len(docs)} chunks indexed.")
    return store


def get_vectorstore() -> FAISS:
    """Return the singleton vector store, building it on first call."""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = _build_vectorstore()
    return _vectorstore


def retrieve_relevant_docs(query: str, k: int = 3) -> list[str]:
    """
    Retrieve the top-k most semantically relevant knowledge-base chunks
    for a given user query.

    Args:
        query: The user's natural-language question
        k:     Number of chunks to return

    Returns:
        List of raw text chunks
    """
    store = get_vectorstore()
    results = store.similarity_search(query, k=k)
    return [doc.page_content for doc in results]
