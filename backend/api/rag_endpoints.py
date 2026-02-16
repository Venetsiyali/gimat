"""
RAG API Endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class RAGQuery(BaseModel):
    question: str
    station_id: Optional[str] = None
    n_results: int = 5


class RAGResponse(BaseModel):
    question: str
    answer: str
    sources: List[dict]
    num_retrieved: int


@router.post("/query", response_model=RAGResponse)
async def rag_query(query: RAGQuery):
    """
    RAG query endpoint - Ask questions about hydrological documents
    
    Args:
        query: RAG query with question and optional context
    
    Returns:
        Answer with sources
    """
    # Placeholder - would use actual RAG pipeline
    from rag.embeddings import HydrologicalEmbedder
    from rag.vector_store import HydroVectorStore
    from rag.retriever import HydroRAGRetriever, ContextBuilder
    from rag.generator import LLMGenerator, HydroRAGPipeline
    
    # Initialize components (in production, these would be singletons)
    embedder = HydrologicalEmbedder()
    vector_store = HydroVectorStore()
    retriever = HydroRAGRetriever(embedder, vector_store)
    generator = LLMGenerator(provider="openai")
    context_builder = ContextBuilder()
    
    pipeline = HydroRAGPipeline(
        embedder, vector_store, retriever, generator, context_builder
    )
    
    # Query
    result = await pipeline.query(
        question=query.question,
        station_id=query.station_id,
        n_results=query.n_results
    )
    
    return RAGResponse(**result)


@router.get("/documents/stats")
async def get_document_stats():
    """Get vector database statistics"""
    from rag.vector_store import HydroVectorStore
    
    vector_store = HydroVectorStore()
    stats = vector_store.get_stats()
    
    return stats
