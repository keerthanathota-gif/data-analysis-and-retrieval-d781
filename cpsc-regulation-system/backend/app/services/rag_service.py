"""
RAG (Retrieval-Augmented Generation) Service for CFR Agentic AI Application
Implements query-based retrieval and similarity search
"""

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import (
    Chapter, Subchapter, Part, Section,
    ChapterEmbedding, SubchapterEmbedding, SectionEmbedding,
    SessionLocal
)
from app.services.embedding_service import EmbeddingService
from app.config import TOP_K_RESULTS

# Create embedding service instance
embedding_service = EmbeddingService()


class RAGService:
    def __init__(self):
        """Initialize RAG service"""
        self.top_k = TOP_K_RESULTS
    
    def query_database(self, query: str, level: str, db: Session, 
                      top_k: int = None) -> List[Dict[str, Any]]:
        """
        Query the database using semantic search
        
        Args:
            query: User query text
            level: One of 'chapter', 'subchapter', 'section', 'all'
            db: Database session
            top_k: Number of top results to return (default: TOP_K_RESULTS)
            
        Returns:
            List of relevant items with similarity scores
        """
        if top_k is None:
            top_k = self.top_k
        
        # Generate query embedding
        query_embedding = embedding_service.generate_embedding(query)
        
        results = []
        
        # Search at specified level
        if level in ['chapter', 'all']:
            chapter_results = self._search_chapters(query_embedding, db, top_k)
            results.extend(chapter_results)
        
        if level in ['subchapter', 'all']:
            subchapter_results = self._search_subchapters(query_embedding, db, top_k)
            results.extend(subchapter_results)
        
        if level in ['section', 'all']:
            section_results = self._search_sections(query_embedding, db, top_k)
            results.extend(section_results)
        
        # Sort by similarity and return top-k
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results[:top_k]
    
    def _search_chapters(self, query_embedding: List[float], db: Session, 
                        top_k: int) -> List[Dict[str, Any]]:
        """Search chapters for relevant content"""
        results = []
        
        chapters = db.query(Chapter).all()
        for chapter in chapters:
            emb = db.query(ChapterEmbedding).filter(
                ChapterEmbedding.chapter_id == chapter.id
            ).first()
            
            if emb:
                similarity = embedding_service.compute_similarity(
                    query_embedding,
                    emb.embedding
                )
                
                results.append({
                    'type': 'chapter',
                    'id': chapter.id,
                    'name': chapter.name,
                    'similarity_score': similarity,
                    'content': chapter.name
                })
        
        return results
    
    def _search_subchapters(self, query_embedding: List[float], db: Session,
                           top_k: int) -> List[Dict[str, Any]]:
        """Search subchapters for relevant content"""
        results = []
        
        subchapters = db.query(Subchapter).all()
        for subchapter in subchapters:
            emb = db.query(SubchapterEmbedding).filter(
                SubchapterEmbedding.subchapter_id == subchapter.id
            ).first()
            
            if emb:
                similarity = embedding_service.compute_similarity(
                    query_embedding,
                    emb.embedding
                )
                
                results.append({
                    'type': 'subchapter',
                    'id': subchapter.id,
                    'name': subchapter.name,
                    'chapter_name': subchapter.chapter.name,
                    'similarity_score': similarity,
                    'content': f"{subchapter.chapter.name} - {subchapter.name}"
                })
        
        return results
    
    def _search_sections(self, query_embedding: List[float], db: Session,
                        top_k: int) -> List[Dict[str, Any]]:
        """Search sections for relevant content"""
        results = []
        
        sections = db.query(Section).all()
        for section in sections:
            emb = db.query(SectionEmbedding).filter(
                SectionEmbedding.section_id == section.id
            ).first()
            
            if emb:
                similarity = embedding_service.compute_similarity(
                    query_embedding,
                    emb.embedding
                )
                
                # Get part and hierarchy info
                part = section.part
                subchapter = part.subchapter if part else None
                chapter = subchapter.chapter if subchapter else None
                
                results.append({
                    'type': 'section',
                    'id': section.id,
                    'section_number': section.section_number,
                    'subject': section.subject,
                    'text': section.text,
                    'citation': section.citation,
                    'section_label': section.section_label,
                    'part_heading': part.heading if part else '',
                    'subchapter_name': subchapter.name if subchapter else '',
                    'chapter_name': chapter.name if chapter else '',
                    'similarity_score': similarity,
                    'content': f"{section.section_number}: {section.subject}\n{section.text}"
                })
        
        return results
    
    def find_similar_by_name(self, name: str, search_type: str, db: Session,
                            top_k: int = None) -> List[Dict[str, Any]]:
        """
        Find similar items by chapter/subchapter/section name
        
        Args:
            name: Name or partial name to search for
            search_type: One of 'chapter', 'subchapter', 'section'
            db: Database session
            top_k: Number of top results to return
            
        Returns:
            List of similar items
        """
        if top_k is None:
            top_k = self.top_k
        
        # First, find the item by name
        target_item = self._find_item_by_name(name, search_type, db)
        
        if not target_item:
            return []
        
        # Get the embedding of the target item
        target_embedding = target_item['embedding']
        
        # Find similar items
        similar_items = self._find_similar_items(
            target_embedding,
            search_type,
            db,
            exclude_id=target_item['id'],
            top_k=top_k
        )
        
        return similar_items
    
    def _find_item_by_name(self, name: str, search_type: str, 
                          db: Session) -> Optional[Dict[str, Any]]:
        """Find an item by name (case-insensitive partial match)"""
        if search_type == 'chapter':
            item = db.query(Chapter).filter(
                Chapter.name.ilike(f"%{name}%")
            ).first()
            
            if item:
                emb = db.query(ChapterEmbedding).filter(
                    ChapterEmbedding.chapter_id == item.id
                ).first()
                
                if emb:
                    return {
                        'id': item.id,
                        'name': item.name,
                        'embedding': emb.embedding
                    }
        
        elif search_type == 'subchapter':
            item = db.query(Subchapter).filter(
                Subchapter.name.ilike(f"%{name}%")
            ).first()
            
            if item:
                emb = db.query(SubchapterEmbedding).filter(
                    SubchapterEmbedding.subchapter_id == item.id
                ).first()
                
                if emb:
                    return {
                        'id': item.id,
                        'name': item.name,
                        'chapter_name': item.chapter.name,
                        'embedding': emb.embedding
                    }
        
        elif search_type == 'section':
            item = db.query(Section).filter(
                or_(
                    Section.section_number.ilike(f"%{name}%"),
                    Section.subject.ilike(f"%{name}%")
                )
            ).first()
            
            if item:
                emb = db.query(SectionEmbedding).filter(
                    SectionEmbedding.section_id == item.id
                ).first()
                
                if emb:
                    return {
                        'id': item.id,
                        'section_number': item.section_number,
                        'subject': item.subject,
                        'text': item.text,
                        'embedding': emb.embedding
                    }
        
        return None
    
    def _find_similar_items(self, target_embedding: str, search_type: str,
                           db: Session, exclude_id: int, top_k: int) -> List[Dict[str, Any]]:
        """Find similar items based on embedding similarity"""
        results = []
        
        if search_type == 'chapter':
            chapters = db.query(Chapter).filter(Chapter.id != exclude_id).all()
            
            for chapter in chapters:
                emb = db.query(ChapterEmbedding).filter(
                    ChapterEmbedding.chapter_id == chapter.id
                ).first()
                
                if emb:
                    similarity = embedding_service.compute_similarity(
                        target_embedding,
                        emb.embedding
                    )
                    
                    results.append({
                        'type': 'chapter',
                        'id': chapter.id,
                        'name': chapter.name,
                        'similarity_score': similarity
                    })
        
        elif search_type == 'subchapter':
            subchapters = db.query(Subchapter).filter(Subchapter.id != exclude_id).all()
            
            for subchapter in subchapters:
                emb = db.query(SubchapterEmbedding).filter(
                    SubchapterEmbedding.subchapter_id == subchapter.id
                ).first()
                
                if emb:
                    similarity = embedding_service.compute_similarity(
                        target_embedding,
                        emb.embedding
                    )
                    
                    results.append({
                        'type': 'subchapter',
                        'id': subchapter.id,
                        'name': subchapter.name,
                        'chapter_name': subchapter.chapter.name,
                        'similarity_score': similarity
                    })
        
        elif search_type == 'section':
            sections = db.query(Section).filter(Section.id != exclude_id).all()
            
            for section in sections:
                emb = db.query(SectionEmbedding).filter(
                    SectionEmbedding.section_id == section.id
                ).first()
                
                if emb:
                    similarity = embedding_service.compute_similarity(
                        target_embedding,
                        emb.embedding
                    )
                    
                    # Get hierarchy info
                    part = section.part
                    subchapter = part.subchapter if part else None
                    chapter = subchapter.chapter if subchapter else None
                    
                    results.append({
                        'type': 'section',
                        'id': section.id,
                        'section_number': section.section_number,
                        'subject': section.subject,
                        'text': section.text,
                        'citation': section.citation,
                        'section_label': section.section_label,
                        'part_heading': part.heading if part else '',
                        'subchapter_name': subchapter.name if subchapter else '',
                        'chapter_name': chapter.name if chapter else '',
                        'similarity_score': similarity
                    })
        
        # Sort by similarity and return top-k
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results[:top_k]
    
    def get_context_for_query(self, query: str, db: Session,
                             max_context_items: int = 5) -> str:
        """
        Get relevant context for a query to use in RAG
        
        Args:
            query: User query
            db: Database session
            max_context_items: Maximum number of context items
            
        Returns:
            Formatted context string
        """
        # Get top relevant items
        results = self.query_database(query, 'all', db, top_k=max_context_items)
        
        # Format context
        context_parts = []
        
        for idx, result in enumerate(results, 1):
            if result['type'] == 'section':
                context = f"[{idx}] Section {result['section_number']}: {result['subject']}\n"
                context += f"{result['text'][:500]}..."  # Truncate long text
            elif result['type'] == 'subchapter':
                context = f"[{idx}] Subchapter: {result['content']}"
            else:
                context = f"[{idx}] {result['type'].title()}: {result['content']}"
            
            context_parts.append(context)
        
        return "\n\n".join(context_parts)


# Global instance
rag_service = RAGService()
