"""
Clustering Service for CFR Agentic AI Application
Implements automatic clustering of overlapping content using HDBSCAN
"""

import json
import numpy as np
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sklearn.cluster import KMeans

from app.models.cfr_database import (
    Chapter, Subchapter, Section, Part,
    ChapterEmbedding, SubchapterEmbedding, SectionEmbedding,
    Cluster, SessionLocal
)
from app.config import CLUSTERING_ALGORITHM, DEFAULT_N_CLUSTERS
from app.services.llm_service import get_llm_service


class ClusteringService:
    def __init__(self):
        """Initialize clustering service - Only K-Means supported"""
        self.algorithm = 'kmeans'
        self.default_n_clusters = DEFAULT_N_CLUSTERS
    
    def cluster_items(self, level: str, db: Session, 
                     n_clusters: int = None) -> Dict[str, Any]:
        """
        Cluster items at specified level using K-Means
        For chapters and subchapters, clustering is based on aggregated section embeddings
        
        Args:
            level: One of 'chapter', 'subchapter', 'section'
            db: Database session
            n_clusters: Number of clusters (default: auto-calculated)
            
        Returns:
            Dictionary with clustering results
        """
        # Get embeddings and items
        embeddings, items = self._get_embeddings_and_items(level, db)
        
        if len(embeddings) == 0:
            return {
                'level': level,
                'algorithm': 'kmeans',
                'num_items': 0,
                'num_clusters': 0,
                'clusters': []
            }
        
        # Convert embeddings to numpy array
        X = np.array(embeddings)
        
        # Perform K-Means clustering
        labels = self._cluster_kmeans(X, n_clusters)
        
        # Process results
        clusters = self._process_clustering_results(
            labels, items, embeddings, level, 'kmeans', None, db
        )
        
        return {
            'level': level,
            'algorithm': 'kmeans',
            'num_items': len(items),
            'num_clusters': len(clusters),
            'clusters': clusters
        }
    
    def _get_embeddings_and_items(self, level: str, db: Session) -> Tuple[List, List]:
        """
        Get embeddings and corresponding items for a level
        For chapters and subchapters, aggregate section embeddings within them
        """
        embeddings = []
        items = []
        
        if level == 'chapter':
            chapters = db.query(Chapter).all()
            for chapter in chapters:
                # Aggregate embeddings from all sections within this chapter
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
                    # Average all section embeddings for this chapter
                    avg_embedding = np.mean(section_embeddings, axis=0).tolist()
                    embeddings.append(avg_embedding)
                    items.append({
                        'id': chapter.id,
                        'name': chapter.name,
                        'type': 'chapter',
                        'num_sections': len(section_embeddings)
                    })
        
        elif level == 'subchapter':
            subchapters = db.query(Subchapter).all()
            for subchapter in subchapters:
                # Aggregate embeddings from all sections within this subchapter
                section_embeddings = []
                for part in subchapter.parts:
                    for section in part.sections:
                        emb = db.query(SectionEmbedding).filter(
                            SectionEmbedding.section_id == section.id
                        ).first()
                        if emb:
                            section_embeddings.append(json.loads(emb.embedding))
                
                if section_embeddings:
                    # Average all section embeddings for this subchapter
                    avg_embedding = np.mean(section_embeddings, axis=0).tolist()
                    embeddings.append(avg_embedding)
                    items.append({
                        'id': subchapter.id,
                        'name': subchapter.name,
                        'chapter_name': subchapter.chapter.name,
                        'type': 'subchapter',
                        'num_sections': len(section_embeddings)
                    })
        
        elif level == 'section':
            sections = db.query(Section).all()
            for section in sections:
                emb = db.query(SectionEmbedding).filter(
                    SectionEmbedding.section_id == section.id
                ).first()
                if emb:
                    embeddings.append(json.loads(emb.embedding))
                    items.append({
                        'id': section.id,
                        'section_number': section.section_number,
                        'subject': section.subject,
                        'type': 'section'
                    })
        
        return embeddings, items
    
    def _cluster_kmeans(self, X: np.ndarray, n_clusters: int = None) -> np.ndarray:
        """Cluster using K-Means algorithm"""
        if n_clusters is None:
            # Estimate number of clusters using elbow method
            n_clusters = min(max(2, len(X) // 10), self.default_n_clusters)
        
        # Ensure n_clusters doesn't exceed number of samples
        n_clusters = min(n_clusters, len(X))
        
        clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = clusterer.fit_predict(X)
        
        return labels
    
    def _process_clustering_results(self, labels: np.ndarray, items: List[Dict],
                                    embeddings: List, level: str, algorithm: str,
                                    probabilities: np.ndarray, db: Session) -> List[Dict]:
        """Process clustering results and store in database"""
        # Group items by cluster
        cluster_dict = {}
        
        for idx, (label, item, embedding) in enumerate(zip(labels, items, embeddings)):
            if label == -1:  # Noise point
                continue
            
            if label not in cluster_dict:
                cluster_dict[label] = {
                    'items': [],
                    'embeddings': []
                }
            
            item_info = item.copy()
            if probabilities is not None:
                item_info['probability'] = float(probabilities[idx])
            
            cluster_dict[label]['items'].append(item_info)
            cluster_dict[label]['embeddings'].append(embedding)
        
        # Process each cluster
        clusters = []
        
        for label, cluster_data in cluster_dict.items():
            items_in_cluster = cluster_data['items']
            embeddings_in_cluster = cluster_data['embeddings']
            
            # Compute centroid
            centroid = np.mean(embeddings_in_cluster, axis=0).tolist()
            
            # Enrich items with actual text content for better LLM summaries
            enriched_items = self._enrich_cluster_items(items_in_cluster, level, db)
            
            # Generate LLM summary and name
            try:
                llm = get_llm_service()
                cluster_summary = llm.generate_cluster_summary(enriched_items, level)
                cluster_name = llm.generate_cluster_name(enriched_items, level, cluster_summary)
            except Exception as e:
                print(f"LLM generation failed for cluster {label}: {e}")
                cluster_summary = f"Cluster of {len(items_in_cluster)} {level}s"
                cluster_name = f"Cluster {label}"
            
            # Store in database
            cluster = Cluster(
                cluster_type=level,
                cluster_label=int(label),
                item_ids=json.dumps([item['id'] for item in items_in_cluster]),
                centroid=json.dumps(centroid),
                size=len(items_in_cluster),
                summary=cluster_summary,
                name=cluster_name
            )
            db.add(cluster)
            
            # Prepare cluster info
            cluster_info = {
                'label': int(label),
                'size': len(items_in_cluster),
                'items': items_in_cluster,
                'centroid': centroid,
                'name': cluster_name,
                'summary': cluster_summary
            }
            
            clusters.append(cluster_info)
        
        db.commit()
        
        # Sort clusters by size (descending)
        clusters.sort(key=lambda x: x['size'], reverse=True)
        
        return clusters
    
    def _enrich_cluster_items(self, items: List[Dict], level: str, db: Session) -> List[Dict]:
        """
        Enrich cluster items with actual text content for better LLM summaries
        
        Args:
            items: List of cluster items
            level: Clustering level
            db: Database session
            
        Returns:
            Enriched items with text content
        """
        enriched = []
        
        for item in items[:5]:  # Limit to first 5 to avoid memory issues
            enriched_item = item.copy()
            
            if level == 'section':
                # Fetch section details
                section = db.query(Section).filter(Section.id == item['id']).first()
                if section:
                    enriched_item['text'] = section.text
                    enriched_item['subject'] = section.subject
                    enriched_item['section_number'] = section.section_number
            
            elif level == 'subchapter':
                # Fetch sample section texts from subchapter
                subchapter = db.query(Subchapter).filter(Subchapter.id == item['id']).first()
                if subchapter:
                    text_parts = []
                    for part in subchapter.parts[:2]:  # First 2 parts
                        for section in part.sections[:2]:  # First 2 sections per part
                            if section.text:
                                text_parts.append(section.text[:150])
                    enriched_item['text'] = " ".join(text_parts)
                    enriched_item['name'] = subchapter.name
            
            elif level == 'chapter':
                # Fetch sample section texts from chapter
                chapter = db.query(Chapter).filter(Chapter.id == item['id']).first()
                if chapter:
                    text_parts = []
                    for subchapter in chapter.subchapters[:2]:  # First 2 subchapters
                        for part in subchapter.parts[:1]:  # First part
                            for section in part.sections[:2]:  # First 2 sections
                                if section.text:
                                    text_parts.append(section.text[:150])
                    enriched_item['text'] = " ".join(text_parts)
                    enriched_item['name'] = chapter.name
            
            enriched.append(enriched_item)
        
        return enriched
    
    def get_cluster_by_id(self, cluster_id: int, db: Session) -> Dict[str, Any]:
        """Get detailed information about a specific cluster"""
        cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()
        
        if not cluster:
            return None
        
        item_ids = json.loads(cluster.item_ids)
        
        # Get full item information
        items = []
        if cluster.cluster_type == 'chapter':
            for item_id in item_ids:
                chapter = db.query(Chapter).filter(Chapter.id == item_id).first()
                if chapter:
                    items.append({
                        'id': chapter.id,
                        'name': chapter.name
                    })
        
        elif cluster.cluster_type == 'subchapter':
            for item_id in item_ids:
                subchapter = db.query(Subchapter).filter(Subchapter.id == item_id).first()
                if subchapter:
                    items.append({
                        'id': subchapter.id,
                        'name': subchapter.name,
                        'chapter_name': subchapter.chapter.name
                    })
        
        elif cluster.cluster_type == 'section':
            for item_id in item_ids:
                section = db.query(Section).filter(Section.id == item_id).first()
                if section:
                    items.append({
                        'id': section.id,
                        'section_number': section.section_number,
                        'subject': section.subject
                    })
        
        return {
            'id': cluster.id,
            'type': cluster.cluster_type,
            'label': cluster.cluster_label,
            'size': cluster.size,
            'items': items,
            'centroid': json.loads(cluster.centroid) if cluster.centroid else None,
            'name': cluster.name,
            'summary': cluster.summary,
            'created_at': cluster.created_at.isoformat()
        }
    
    def get_all_clusters(self, level: str, db: Session) -> List[Dict[str, Any]]:
        """Get all clusters for a specific level"""
        clusters = db.query(Cluster).filter(Cluster.cluster_type == level).all()
        
        return [
            {
                'id': cluster.id,
                'label': cluster.cluster_label,
                'size': cluster.size,
                'item_ids': json.loads(cluster.item_ids),
                'name': cluster.name,
                'summary': cluster.summary
            }
            for cluster in clusters
        ]


# Global instance
clustering_service = ClusteringService()
