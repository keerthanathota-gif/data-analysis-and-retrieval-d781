"""
Embedding Service for CFR Agentic AI Application
Uses sentence-transformers for generating embeddings
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import json
from app.config import EMBEDDING_MODEL, EMBEDDING_DIMENSION

class EmbeddingService:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize the embedding service with a sentence transformer model"""
        self.model = SentenceTransformer(model_name)
        self.dimension = EMBEDDING_DIMENSION
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding
        """
        if not text or not text.strip():
            return [0.0] * self.dimension
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        # Replace empty strings with placeholder
        processed_texts = [text if text and text.strip() else " " for text in texts]
        
        embeddings = self.model.encode(processed_texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()
    
    def compute_similarity(self, embedding1: Union[List[float], str], 
                          embedding2: Union[List[float], str]) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding (list or JSON string)
            embedding2: Second embedding (list or JSON string)
            
        Returns:
            Similarity score between 0 and 1
        """
        # Parse JSON strings if necessary
        if isinstance(embedding1, str):
            embedding1 = json.loads(embedding1)
        if isinstance(embedding2, str):
            embedding2 = json.loads(embedding2)
        
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Compute cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    def compute_similarity_matrix(self, embeddings: List[Union[List[float], str]]) -> np.ndarray:
        """
        Compute similarity matrix for a list of embeddings
        
        Args:
            embeddings: List of embeddings
            
        Returns:
            Similarity matrix as numpy array
        """
        # Parse JSON strings if necessary
        parsed_embeddings = []
        for emb in embeddings:
            if isinstance(emb, str):
                parsed_embeddings.append(json.loads(emb))
            else:
                parsed_embeddings.append(emb)
        
        # Convert to numpy array
        emb_matrix = np.array(parsed_embeddings)
        
        # Compute cosine similarity matrix
        norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
        normalized = emb_matrix / np.maximum(norms, 1e-10)
        similarity_matrix = np.dot(normalized, normalized.T)
        
        return similarity_matrix
    
    def find_similar_items(self, query_embedding: Union[List[float], str],
                          candidate_embeddings: List[Union[List[float], str]],
                          top_k: int = 10) -> List[tuple]:
        """
        Find top-k most similar items to the query
        
        Args:
            query_embedding: Query embedding
            candidate_embeddings: List of candidate embeddings
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples sorted by similarity
        """
        # Parse query embedding
        if isinstance(query_embedding, str):
            query_embedding = json.loads(query_embedding)
        
        query_vec = np.array(query_embedding)
        
        # Compute similarities
        similarities = []
        for idx, candidate in enumerate(candidate_embeddings):
            if isinstance(candidate, str):
                candidate = json.loads(candidate)
            
            candidate_vec = np.array(candidate)
            similarity = self.compute_similarity(query_vec.tolist(), candidate_vec.tolist())
            similarities.append((idx, similarity))
        
        # Sort by similarity (descending) and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

# Global instance
embedding_service = EmbeddingService()
