"""
Vector Store using ChromaDB
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid


class HydroVectorStore:
    """
    Vector database for hydrological documents
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB client
        
        Args:
            persist_directory: Path to persist database
        """
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))
        
        # Create collections
        self.normative_collection = self.client.get_or_create_collection(
            name="normative_documents",
            metadata={"description": "Gidrologik normativ hujjatlar"}
        )
        
        self.reports_collection = self.client.get_or_create_collection(
            name="technical_reports",
            metadata={"description": "Texnik hisobotlar va byulletenlar"}
        )
        
        self.archive_collection = self.client.get_or_create_collection(
            name="historical_archive",
            metadata={"description": "Tarixiy arxiv"}
        )
    
    def add_documents(self, 
                     documents: List[str],
                     metadatas: List[Dict],
                     embeddings: List[List[float]],
                     collection_name: str = "normative_documents") -> List[str]:
        """
        Add documents to vector store
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dicts
            embeddings: List of embedding vectors
            collection_name: Target collection
        
        Returns:
            List of document IDs
        """
        collection = self._get_collection(collection_name)
        
        # Generate IDs
        ids = [str(uuid.uuid4()) for _ in documents]
        
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def search(self,
              query_embedding: List[float],
              collection_name: str = "normative_documents",
              n_results: int = 5,
              where: Optional[Dict] = None) -> Dict:
        """
        Semantic search
        
        Args:
            query_embedding: Query embedding vector
            collection_name: Collection to search
            n_results: Number of results
            where: Metadata filters
        
        Returns:
            Search results with documents and metadata
        """
        collection = self._get_collection(collection_name)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        return results
    
    def get_by_metadata(self,
                       where: Dict,
                       collection_name: str = "normative_documents") -> Dict:
        """
        Get documents by metadata filter
        
        Args:
            where: Metadata filter dict
            collection_name: Collection name
        
        Returns:
            Matching documents
        """
        collection = self._get_collection(collection_name)
        
        results = collection.get(where=where)
        return results
    
    def delete_documents(self,
                        ids: List[str],
                        collection_name: str = "normative_documents"):
        """Delete documents by IDs"""
        collection = self._get_collection(collection_name)
        collection.delete(ids=ids)
    
    def _get_collection(self, collection_name: str):
        """Get collection by name"""
        if collection_name == "normative_documents":
            return self.normative_collection
        elif collection_name == "technical_reports":
            return self.reports_collection
        elif collection_name == "historical_archive":
            return self.archive_collection
        else:
            raise ValueError(f"Unknown collection: {collection_name}")
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return {
            'normative_count': self.normative_collection.count(),
            'reports_count': self.reports_collection.count(),
            'archive_count': self.archive_collection.count()
        }


# ==========================================
# Document Processor
# ==========================================

class DocumentProcessor:
    """Process PDFs and documents for RAG"""
    
    def __init__(self):
        pass
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Extract text from PDF
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Processed document dict
        """
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                metadata = {
                    'filename': pdf_path,
                    'num_pages': len(pdf_reader.pages),
                    'type': 'pdf'
                }
                
                return {
                    'text': text,
                    'metadata': metadata
                }
        
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text
            chunk_size: Characters per chunk
            overlap: Overlapping characters
        
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
