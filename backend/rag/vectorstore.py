"""
vectorstore.py – FAISS vector store management with robust error handling.

Implements thread-safe singleton pattern for efficient vector store initialization
and provides semantic search capabilities over the AutoStream knowledge base.
"""

import threading
from typing import Optional
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from rag.loader import load_knowledge_base, KnowledgeBaseValidationError
from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)

# Thread-safe singleton pattern for vector store
_vectorstore: Optional[FAISS] = None
_vectorstore_lock = threading.Lock()
_initialization_failed = False
_initialization_error: Optional[Exception] = None


class VectorStoreInitializationError(Exception):
    """Raised when vector store initialization fails."""
    pass


def _build_vectorstore() -> FAISS:
    """
    Embed all knowledge-base chunks and store them in a local FAISS index.
    Uses the lightweight all-MiniLM-L6-v2 sentence-transformer model so the
    project runs without any external embedding API key.
    
    Returns:
        Initialized FAISS vector store
        
    Raises:
        VectorStoreInitializationError: If initialization fails
    """
    logger.info(
        "Starting FAISS vector store initialization",
        extra={"embedding_model": settings.EMBEDDING_MODEL}
    )
    
    try:
        # Step 1: Load knowledge base chunks
        logger.info("Loading knowledge base chunks")
        chunks = load_knowledge_base()
        logger.info(
            "Knowledge base loaded successfully",
            extra={"num_chunks": len(chunks)}
        )
        
        # Step 2: Convert to LangChain documents
        docs = [Document(page_content=chunk) for chunk in chunks]
        logger.info("Converted chunks to document format")
        
        # Step 3: Initialize embedding model
        logger.info(
            "Initializing embedding model",
            extra={"model": settings.EMBEDDING_MODEL}
        )
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("Embedding model initialized successfully")
        
        # Step 4: Build FAISS index
        logger.info("Building FAISS index from documents")
        store = FAISS.from_documents(docs, embeddings)
        
        logger.info(
            "Vector store initialization complete",
            extra={
                "num_chunks": len(docs),
                "embedding_model": settings.EMBEDDING_MODEL,
                "status": "ready"
            }
        )
        return store
        
    except KnowledgeBaseValidationError as e:
        logger.error(
            "Knowledge base validation failed during vector store initialization",
            extra={
                "error_type": "KnowledgeBaseValidationError",
                "error_message": str(e)
            }
        )
        raise VectorStoreInitializationError(
            f"Knowledge base validation failed: {e}"
        ) from e
        
    except FileNotFoundError as e:
        logger.error(
            "Knowledge base file not found during vector store initialization",
            extra={
                "error_type": "FileNotFoundError",
                "error_message": str(e)
            }
        )
        raise VectorStoreInitializationError(
            f"Knowledge base file not found: {e}"
        ) from e
        
    except Exception as e:
        logger.error(
            "Unexpected error during vector store initialization",
            extra={
                "error_type": type(e).__name__,
                "error_message": str(e)
            },
            exc_info=True
        )
        raise VectorStoreInitializationError(
            f"Failed to initialize vector store: {e}"
        ) from e


def get_vectorstore() -> FAISS:
    """
    Return the singleton vector store, building it on first call.
    
    This function implements a thread-safe singleton pattern to ensure
    the vector store is only initialized once, even in concurrent environments.
    
    Returns:
        Initialized FAISS vector store
        
    Raises:
        VectorStoreInitializationError: If initialization failed previously or fails now
    """
    global _vectorstore, _initialization_failed, _initialization_error
    
    # Fast path: vector store already initialized
    if _vectorstore is not None:
        return _vectorstore
    
    # Fast path: initialization previously failed
    if _initialization_failed:
        logger.warning(
            "Vector store initialization previously failed, returning cached error",
            extra={"cached_error": str(_initialization_error)}
        )
        raise VectorStoreInitializationError(
            f"Vector store initialization failed previously: {_initialization_error}"
        ) from _initialization_error
    
    # Slow path: need to initialize (thread-safe)
    with _vectorstore_lock:
        # Double-check pattern: another thread might have initialized while we waited
        if _vectorstore is not None:
            logger.info("Vector store already initialized by another thread")
            return _vectorstore
        
        if _initialization_failed:
            raise VectorStoreInitializationError(
                f"Vector store initialization failed previously: {_initialization_error}"
            ) from _initialization_error
        
        try:
            logger.info("Acquiring lock for vector store initialization")
            _vectorstore = _build_vectorstore()
            logger.info("Vector store singleton initialized successfully")
            return _vectorstore
            
        except Exception as e:
            # Cache the failure to avoid repeated initialization attempts
            _initialization_failed = True
            _initialization_error = e
            logger.error(
                "Vector store initialization failed, caching error state",
                extra={
                    "error_type": type(e).__name__,
                    "will_retry": False
                }
            )
            raise


def retrieve_relevant_docs(query: str, k: int = 3) -> list[str]:
    """
    Retrieve the top-k most semantically relevant knowledge-base chunks
    for a given user query.

    Args:
        query: The user's natural-language question
        k:     Number of chunks to return

    Returns:
        List of raw text chunks
        
    Raises:
        VectorStoreInitializationError: If vector store initialization fails
    """
    try:
        store = get_vectorstore()
        results = store.similarity_search(query, k=k)
        
        logger.info(
            "Retrieved relevant documents",
            extra={
                "query_length": len(query),
                "num_results": len(results),
                "k": k
            }
        )
        
        return [doc.page_content for doc in results]
        
    except VectorStoreInitializationError:
        logger.error(
            "Cannot retrieve documents: vector store initialization failed",
            extra={"query": query[:100]}  # Log first 100 chars of query
        )
        raise
