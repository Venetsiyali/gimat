"""
LLM Response Generator for RAG
"""

from typing import Dict, Optional
import os


class LLMGenerator:
    """
    Generate responses using LLM (OpenAI GPT or local model)
    """
    
    def __init__(self, provider: str = "openai", model: str = "gpt-4"):
        """
        Initialize LLM generator
        
        Args:
            provider: 'openai' or 'local'
            model: Model name
        """
        self.provider = provider
        self.model = model
        
        if provider == "openai":
            import openai
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif provider == "local":
            # Placeholder for local model (Llama, etc.)
            print("Local LLM not implemented yet, using mock")
            self.client = None
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate response
        
        Args:
            prompt: Complete prompt with context
            max_tokens: Maximum response length
        
        Returns:
            Generated text
        """
        if self.provider == "openai" and self.client:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Siz gidrologiya mutaxassisisiz."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        else:
            # Mock response for development
            return f"[Mock Response] Bu RAG tizimi orqali generatsiya qilingan javob. Prompt: {prompt[:100]}..."
    
    def generate_with_citations(self, prompt: str, retrieved_docs: list) -> Dict:
        """
        Generate response with source citations
        
        Args:
            prompt: Complete prompt
            retrieved_docs: Retrieved documents for citation
        
        Returns:
            Response with citations
        """
        response_text = self.generate(prompt)
        
        # Add citations
        citations = []
        for i, doc in enumerate(retrieved_docs[:3]):
            metadata = doc.get('metadata', {})
            citations.append({
                'source': metadata.get('filename', f'Document {i+1}'),
                'relevance': doc.get('relevance_score', 0.0)
            })
        
        return {
            'answer': response_text,
            'citations': citations
        }


# ==========================================
# Complete RAG Pipeline
# ==========================================

class HydroRAGPipeline:
    """
    Complete RAG pipeline: Query → Retrieve → Generate
    """
    
    def __init__(self,
                 embedder,
                 vector_store,
                 retriever,
                 generator: LLMGenerator,
                 context_builder):
        """Initialize RAG pipeline"""
        self.embedder = embedder
        self.vector_store = vector_store
        self.retriever = retriever
        self.generator = generator
        self.context_builder = context_builder
    
    async def query(self,
                   question: str,
                   station_id: Optional[str] = None,
                   n_results: int = 5) -> Dict:
        """
        Process RAG query end-to-end
        
        Args:
            question: User question
            station_id: Optional station for context
            n_results: Number of retrieved docs
        
        Returns:
            Complete response with answer and sources
        """
        # Step 1: Retrieve
        retrieved = await self.retriever.retrieve(
            query=question,
            n_results=n_results,
            station_id=station_id
        )
        
        # Step 2: Rank
        ranked_docs = self.retriever.rank_results(retrieved, question)
        
        # Step 3: Build prompt
        prompt = self.context_builder.build_prompt(
            query=question,
            retrieved_docs=ranked_docs,
            graph_context=retrieved.get('graph')
        )
        
        # Step 4: Generate
        response = self.generator.generate_with_citations(prompt, ranked_docs)
        
        return {
            'question': question,
            'answer': response['answer'],
            'sources': response['citations'],
            'num_retrieved': len(ranked_docs)
        }
