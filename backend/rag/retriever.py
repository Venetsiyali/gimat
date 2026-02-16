"""
RAG Retriever - Semantic Search and Context Building
"""

from rag.embeddings import HydrologicalEmbedder
from rag.vector_store import HydroVectorStore
from typing import List, Dict, Optional
import asyncio
from database.neo4j_db import Neo4jManager
from database.timescale import get_session


class HydroRAGRetriever:
    """
    Intelligent retriever combining vector search with graph context
    """
    
    def __init__(self, 
                 embedder: HydrologicalEmbedder,
                 vector_store: HydroVectorStore,
                 neo4j_manager: Optional[Neo4jManager] = None):
        """
        Initialize retriever
        
        Args:
            embedder: Embedding model
            vector_store: Vector database
            neo4j_manager: Neo4j graph database
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.neo4j = neo4j_manager
    
    async def retrieve(self,
                      query: str,
                      n_results: int = 5,
                      include_graph_context: bool = True,
                      station_id: Optional[str] = None) -> Dict:
        """
        Retrieve relevant documents and context
        
        Args:
            query: User question
            n_results: Number of documents to retrieve
            include_graph_context: Include graph data
            station_id: Specific station for context
        
        Returns:
            Retrieved documents and context
        """
        # Embed query
        query_embedding = self.embedder.embed_text(query)[0]
        
        # Semantic search in vector store
        search_results = self.vector_store.search(
            query_embedding=query_embedding.tolist(),
            n_results=n_results
        )
        
        # Build context
        context = {
            'documents': search_results['documents'][0] if search_results['documents'] else [],
            'metadatas': search_results['metadatas'][0] if search_results['metadatas'] else [],
            'distances': search_results['distances'][0] if search_results['distances'] else []
        }
        
        # Add graph context
        if include_graph_context and self.neo4j and station_id:
            graph_context = await self._get_graph_context(station_id)
            context['graph'] = graph_context
        
        return context
    
    async def _get_graph_context(self, station_id: str) -> Dict:
        """Get relevant graph context from Neo4j"""
        if not self.neo4j:
            return {}
        
        # Get upstream and downstream stations
        upstream = await self.neo4j.get_upstream_stations(station_id)
        downstream = await self.neo4j.get_downstream_stations(station_id)
        
        return {
            'station_id': station_id,
            'upstream_stations': upstream,
            'downstream_stations': downstream
        }
    
    def rank_results(self, results: Dict, query: str) -> List[Dict]:
        """
        Re-rank results based on relevance
        
        Args:
            results: Retrieved results
            query: Original query
        
        Returns:
            Ranked results
        """
        ranked = []
        
        for doc, metadata, distance in zip(
            results['documents'],
            results['metadatas'],
            results['distances']
        ):
            score = 1 / (1 + distance)  # Convert distance to similarity
            
            ranked.append({
                'document': doc,
                'metadata': metadata,
                'relevance_score': score
            })
        
        # Sort by score
        ranked.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return ranked


# ==========================================
# Context Builder
# ==========================================

class ContextBuilder:
    """
    Build comprehensive context for LLM
    """
    
    def __init__(self):
        pass
    
    def build_prompt(self,
                    query: str,
                    retrieved_docs: List[Dict],
                    graph_context: Optional[Dict] = None,
                    system_role: str = "hydrological_expert") -> str:
        """
        Build prompt for LLM
        
        Args:
            query: User question
            retrieved_docs: Retrieved documents
            graph_context: Graph database context
            system_role: AI role
        
        Returns:
            Complete prompt
        """
        # System message
        if system_role == "hydrological_expert":
            system_msg = """Siz gidrologiya bo'yicha mutaxassis sun'iy intellektsiz. 
            O'zbekiston daryo havzalari, normativ hujjatlar va texnik standartlar haqida 
            chuqur bilimga egasiz. Savolga aniq, ilmiy asoslangan javob bering."""
        else:
            system_msg = "Siz yordamchi AIsiz."
        
        # Document context
        doc_context = "\n\n".join([
            f"Hujjat {i+1}:\n{doc['document']}"
            for i, doc in enumerate(retrieved_docs[:3])  # Top 3
        ])
        
        # Graph context
        graph_info = ""
        if graph_context:
            graph_info = f"\n\nGidropost ma'lumotlari:\n"
            graph_info += f"Station: {graph_context.get('station_id', 'N/A')}\n"
            if graph_context.get('upstream_stations'):
                graph_info += f"Yuqori oqim: {len(graph_context['upstream_stations'])} ta post\n"
            if graph_context.get('downstream_stations'):
                graph_info += f"Quyi oqim: {len(graph_context['downstream_stations'])} ta post\n"
        
        # Build full prompt
        prompt = f"""{system_msg}

Quyidagi hujjatlar asosida savolga javob bering:

{doc_context}
{graph_info}

Savol: {query}

Javob:"""
        
        return prompt
