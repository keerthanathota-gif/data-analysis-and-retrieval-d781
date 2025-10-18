"""
Analysis Service for CFR Agentic AI Application
Handles semantic similarity, overlap detection, redundancy, and parity checks
"""

import json
import numpy as np
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.database import (
    Chapter, Subchapter, Section,
    ChapterEmbedding, SubchapterEmbedding, SectionEmbedding,
    SimilarityResult, ParityCheck, SessionLocal
)
from app.services.embedding_service import EmbeddingService
from app.config import SIMILARITY_THRESHOLD, OVERLAP_THRESHOLD, REDUNDANCY_THRESHOLD

# Create embedding service instance
embedding_service = EmbeddingService()


class AnalysisService:
    def __init__(self):
        """Initialize analysis service"""
        self.similarity_threshold = SIMILARITY_THRESHOLD
        self.overlap_threshold = OVERLAP_THRESHOLD
        self.redundancy_threshold = REDUNDANCY_THRESHOLD
    
    def analyze_semantic_similarity(self, level: str, db: Session) -> List[Dict[str, Any]]:
        """
        Analyze semantic similarity at specified level (chapter/subchapter/section)
        
        Args:
            level: One of 'chapter', 'subchapter', 'section'
            db: Database session
            
        Returns:
            List of similarity results
        """
        results = []
        
        if level == "chapter":
            results = self._analyze_chapter_similarity(db)
        elif level == "subchapter":
            results = self._analyze_subchapter_similarity(db)
        elif level == "section":
            results = self._analyze_section_similarity(db)
        else:
            raise ValueError(f"Invalid level: {level}. Must be 'chapter', 'subchapter', or 'section'")
        
        return results
    
    def _analyze_chapter_similarity(self, db: Session) -> List[Dict[str, Any]]:
        """
        Analyze similarity between chapters based on their sections
        Chapter similarity is computed from aggregated section embeddings
        """
        chapters = db.query(Chapter).all()
        embeddings_data = []
        
        # Collect and aggregate section embeddings for each chapter
        for chapter in chapters:
            section_embeddings = []
            for subchapter in chapter.subchapters:
                for part in subchapter.parts:
                    for section in part.sections:
                        emb = db.query(SectionEmbedding).filter(
                            SectionEmbedding.section_id == section.id
                        ).first()
                        if emb:
                            section_embeddings.append(json.loads(emb.embedding))
            
            if section_embeddings:
                # Average all section embeddings
                avg_embedding = np.mean(section_embeddings, axis=0).tolist()
                embeddings_data.append({
                    'id': chapter.id,
                    'name': chapter.name,
                    'embedding': json.dumps(avg_embedding),
                    'num_sections': len(section_embeddings)
                })
        
        print(f"Analyzing chapter similarity...")
        return self._compute_pairwise_similarity(embeddings_data, 'chapter', db, max_comparisons=500)
    
    def _analyze_subchapter_similarity(self, db: Session) -> List[Dict[str, Any]]:
        """
        Analyze similarity between subchapters based on their sections
        Subchapter similarity is computed from aggregated section embeddings
        """
        subchapters = db.query(Subchapter).all()
        embeddings_data = []
        
        # Collect and aggregate section embeddings for each subchapter
        for subchapter in subchapters:
            section_embeddings = []
            for part in subchapter.parts:
                for section in part.sections:
                    emb = db.query(SectionEmbedding).filter(
                        SectionEmbedding.section_id == section.id
                    ).first()
                    if emb:
                        section_embeddings.append(json.loads(emb.embedding))
            
            if section_embeddings:
                # Average all section embeddings
                avg_embedding = np.mean(section_embeddings, axis=0).tolist()
                embeddings_data.append({
                    'id': subchapter.id,
                    'name': subchapter.name,
                    'chapter_name': subchapter.chapter.name,
                    'embedding': json.dumps(avg_embedding),
                    'num_sections': len(section_embeddings)
                })
        
        print(f"Analyzing subchapter similarity...")
        return self._compute_pairwise_similarity(embeddings_data, 'subchapter', db, max_comparisons=1000)
    
    def _analyze_section_similarity(self, db: Session) -> List[Dict[str, Any]]:
        """Analyze similarity between sections"""
        sections = db.query(Section).all()
        embeddings_data = []
        
        # Collect embeddings
        for section in sections:
            emb = db.query(SectionEmbedding).filter(SectionEmbedding.section_id == section.id).first()
            if emb:
                embeddings_data.append({
                    'id': section.id,
                    'section_number': section.section_number,
                    'subject': section.subject,
                    'embedding': emb.embedding
                })
        
        return self._compute_pairwise_similarity(embeddings_data, 'section', db)
    
    def _compute_pairwise_similarity(self, embeddings_data: List[Dict], 
                                    item_type: str, db: Session) -> List[Dict[str, Any]]:
        """Compute pairwise similarity for all items"""
        results = []
        n = len(embeddings_data)
        
        for i in range(n):
            for j in range(i + 1, n):
                item1 = embeddings_data[i]
                item2 = embeddings_data[j]
                
                # Compute similarity
                similarity = embedding_service.compute_similarity(
                    item1['embedding'],
                    item2['embedding']
                )
                
                # Determine overlap and redundancy
                is_overlap = similarity >= self.overlap_threshold
                is_redundant = similarity >= self.redundancy_threshold
                
                # Store in database
                sim_result = SimilarityResult(
                    item1_type=item_type,
                    item1_id=item1['id'],
                    item2_type=item_type,
                    item2_id=item2['id'],
                    similarity_score=similarity,
                    is_overlap=is_overlap,
                    is_redundant=is_redundant
                )
                db.add(sim_result)
                
                # Add to results if above threshold
                if similarity >= self.similarity_threshold:
                    result = {
                        'item1_id': item1['id'],
                        'item2_id': item2['id'],
                        'similarity_score': similarity,
                        'is_overlap': is_overlap,
                        'is_redundant': is_redundant
                    }
                    
                    # Add names based on type
                    if item_type == 'chapter':
                        result['item1_name'] = item1['name']
                        result['item2_name'] = item2['name']
                    elif item_type == 'subchapter':
                        result['item1_name'] = f"{item1['chapter_name']} - {item1['name']}"
                        result['item2_name'] = f"{item2['chapter_name']} - {item2['name']}"
                    elif item_type == 'section':
                        result['item1_name'] = f"{item1['section_number']}: {item1['subject']}"
                        result['item2_name'] = f"{item2['section_number']}: {item2['subject']}"
                    
                    results.append(result)
        
        db.commit()
        print(f"  ✓ Found {len(results)} similar pairs (from {comparisons_done} comparisons)")
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results
    
    def check_overlaps(self, level: str, db: Session) -> List[Dict[str, Any]]:
        """
        Check for overlaps at specified level
        
        Args:
            level: One of 'chapter', 'subchapter', 'section'
            db: Database session
            
        Returns:
            List of overlapping items
        """
        overlaps = db.query(SimilarityResult).filter(
            and_(
                SimilarityResult.item1_type == level,
                SimilarityResult.is_overlap == True
            )
        ).all()
        
        return [
            {
                'item1_id': o.item1_id,
                'item2_id': o.item2_id,
                'similarity_score': o.similarity_score
            }
            for o in overlaps
        ]
    
    def check_redundancy(self, level: str, db: Session) -> List[Dict[str, Any]]:
        """
        Check for redundancy at specified level
        
        Args:
            level: One of 'chapter', 'subchapter', 'section'
            db: Database session
            
        Returns:
            List of redundant items
        """
        redundancies = db.query(SimilarityResult).filter(
            and_(
                SimilarityResult.item1_type == level,
                SimilarityResult.is_redundant == True
            )
        ).all()
        
        return [
            {
                'item1_id': r.item1_id,
                'item2_id': r.item2_id,
                'similarity_score': r.similarity_score
            }
            for r in redundancies
        ]
    
    def perform_parity_check(self, level: str, db: Session) -> List[Dict[str, Any]]:
        """
        Perform parity checks (consistency checks) at specified level
        
        Args:
            level: One of 'chapter', 'subchapter', 'section'
            db: Database session
            
        Returns:
            List of parity check results
        """
        results = []
        
        if level == "chapter":
            chapters = db.query(Chapter).all()
            for chapter in chapters:
                # Check if chapter has subchapters
                has_subchapters = len(chapter.subchapters) > 0
                
                parity_check = ParityCheck(
                    item_type='chapter',
                    item_id=chapter.id,
                    check_type='has_subchapters',
                    result=has_subchapters,
                    details=json.dumps({'subchapter_count': len(chapter.subchapters)})
                )
                db.add(parity_check)
                
                results.append({
                    'item_id': chapter.id,
                    'item_name': chapter.name,
                    'check_type': 'has_subchapters',
                    'result': has_subchapters,
                    'subchapter_count': len(chapter.subchapters)
                })
        
        elif level == "subchapter":
            subchapters = db.query(Subchapter).all()
            for subchapter in subchapters:
                # Check if subchapter has parts
                has_parts = len(subchapter.parts) > 0
                
                parity_check = ParityCheck(
                    item_type='subchapter',
                    item_id=subchapter.id,
                    check_type='has_parts',
                    result=has_parts,
                    details=json.dumps({'part_count': len(subchapter.parts)})
                )
                db.add(parity_check)
                
                results.append({
                    'item_id': subchapter.id,
                    'item_name': subchapter.name,
                    'check_type': 'has_parts',
                    'result': has_parts,
                    'part_count': len(subchapter.parts)
                })
        
        elif level == "section":
            sections = db.query(Section).all()
            for section in sections:
                # Check if section has text
                has_text = bool(section.text and section.text.strip())
                
                parity_check = ParityCheck(
                    item_type='section',
                    item_id=section.id,
                    check_type='has_text',
                    result=has_text,
                    details=json.dumps({'text_length': len(section.text) if section.text else 0})
                )
                db.add(parity_check)
                
                results.append({
                    'item_id': section.id,
                    'item_name': f"{section.section_number}: {section.subject}",
                    'check_type': 'has_text',
                    'result': has_text,
                    'text_length': len(section.text) if section.text else 0
                })
        
        db.commit()
        return results
    
    def get_analysis_summary(self, level: str, db: Session) -> Dict[str, Any]:
        """
        Get a summary of all analyses for a given level
        
        Args:
            level: One of 'chapter', 'subchapter', 'section'
            db: Database session
            
        Returns:
            Dictionary with analysis summary
        """
        # Count items
        if level == "chapter":
            item_count = db.query(Chapter).count()
        elif level == "subchapter":
            item_count = db.query(Subchapter).count()
        elif level == "section":
            item_count = db.query(Section).count()
        else:
            item_count = 0
        
        # Count similarity results
        similarity_count = db.query(SimilarityResult).filter(
            SimilarityResult.item1_type == level
        ).count()
        
        # Count overlaps
        overlap_count = db.query(SimilarityResult).filter(
            and_(
                SimilarityResult.item1_type == level,
                SimilarityResult.is_overlap == True
            )
        ).count()
        
        # Count redundancies
        redundancy_count = db.query(SimilarityResult).filter(
            and_(
                SimilarityResult.item1_type == level,
                SimilarityResult.is_redundant == True
            )
        ).count()
        
        # Count parity checks
        parity_check_count = db.query(ParityCheck).filter(
            ParityCheck.item_type == level
        ).count()
        
        return {
            'level': level,
            'item_count': item_count,
            'similarity_pairs': similarity_count,
            'overlaps': overlap_count,
            'redundancies': redundancy_count,
            'parity_checks': parity_check_count
        }


# Global instance
analysis_service = AnalysisService()
