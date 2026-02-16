"""
Document Embedding Module
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union


class HydrologicalEmbedder:
    """
    Embedding model for hydrological documents
    Supports Uzbek, Russian, and English
    """
    
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Initialize embedding model
        
        Args:
            model_name: Sentence transformer model name
        """
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Embed text or list of texts
        
        Args:
            text: Single text or list of texts
        
        Returns:
            Numpy array of embeddings
        """
        if isinstance(text, str):
            text = [text]
        
        embeddings = self.model.encode(text, convert_to_numpy=True)
        return embeddings
    
    def embed_document(self, document: str, chunk_size: int = 512) -> List[np.ndarray]:
        """
        Embed long document by chunking
        
        Args:
            document: Long text document
            chunk_size: Characters per chunk
        
        Returns:
            List of embeddings for each chunk
        """
        chunks = self._chunk_document(document, chunk_size)
        embeddings = self.embed_text(chunks)
        return embeddings
    
    def _chunk_document(self, document: str, chunk_size: int) -> List[str]:
        """Split document into chunks"""
        words = document.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # +1 for space
            
            if current_size + word_size > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks


# ==========================================
# Specialized Embedders
# ==========================================

class NormativeDocumentEmbedder(HydrologicalEmbedder):
    """Specialized for normative documents"""
    
    def preprocess_text(self, text: str) -> str:
        """Clean normative document text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Normalize Cyrillic/Latin
        # (placeholder - real implementation would use transliteration)
        
        return text


class TechnicalReportEmbedder(HydrologicalEmbedder):
    """Specialized for technical reports"""
    
    def extract_metadata(self, text: str) -> dict:
        """Extract metadata from report"""
        metadata = {
            'has_tables': 'таблица' in text.lower() or 'table' in text.lower(),
            'has_graphs': 'график' in text.lower() or 'график' in text.lower(),
            'has_equations': '=' in text
        }
        return metadata
