"""
Network Analysis Service for CFR Regulations
Combines semantic similarity and citation analysis for network graphs
"""

import json
import numpy as np
from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session
from collections import defaultdict

from app.models.database import Section, SectionEmbedding
from app.services.citation_service import citation_service
from app.services.embedding_service import EmbeddingService


class NetworkService:
    """Service for building and analyzing regulation networks"""
    
    def __init__(self):
        """Initialize network service"""
        self.embedding_service = EmbeddingService()
        self.citation_service = citation_service
    
    def build_semantic_network(self, db: Session, 
                               similarity_threshold: float = 0.75,
                               max_sections: Optional[int] = None) -> Dict[str, Any]:
        """
        Build semantic network graph combining similarity and citations
        
        Args:
            db: Database session
            similarity_threshold: Minimum similarity to create edge
            max_sections: Limit number of sections (for performance)
            
        Returns:
            Network graph data with nodes, edges, and clusters
        """
        print(f"Building semantic network (threshold: {similarity_threshold})...")
        
        # Get sections
        query = db.query(Section)
        if max_sections:
            query = query.limit(max_sections)
        sections = query.all()
        
        print(f"  Processing {len(sections)} sections")
        
        # Get embeddings
        embeddings_data = []
        for section in sections:
            emb = db.query(SectionEmbedding).filter(
                SectionEmbedding.section_id == section.id
            ).first()
            
            if emb:
                embeddings_data.append({
                    'section': section,
                    'embedding': json.loads(emb.embedding) if isinstance(emb.embedding, str) else emb.embedding
                })
        
        print(f"  Found {len(embeddings_data)} sections with embeddings")
        
        # Build citation graph
        citation_graph = self.citation_service.build_citation_graph(db)
        
        # Calculate PageRank
        pagerank_scores = self.citation_service.calculate_pagerank(citation_graph)
        
        # Build nodes with combined metrics
        nodes = []
        node_lookup = {}
        
        for i, data in enumerate(embeddings_data):
            section = data['section']
            section_num = section.section_number
            
            # Get citation info
            citation_node = next(
                (n for n in citation_graph['nodes'] if n['id'] == section_num), 
                None
            )
            
            citations_in = citation_node['citations_in'] if citation_node else 0
            citations_out = citation_node['citations_out'] if citation_node else 0
            
            # Calculate importance (combination of citations and PageRank)
            pagerank = pagerank_scores.get(section_num, 0)
            importance = (citations_in * 2 + citations_out + pagerank * 100) / 4
            
            node = {
                'id': section_num,
                'label': section_num,
                'subject': section.subject or 'No subject',
                'citation': section.citation or '',
                'text_preview': (section.text[:200] + '...') if section.text else '',
                'text_length': len(section.text) if section.text else 0,
                'citations_in': citations_in,
                'citations_out': citations_out,
                'pagerank': round(pagerank, 6),
                'importance': round(importance, 2),
                'index': i  # For embedding lookup
            }
            nodes.append(node)
            node_lookup[section_num] = node
        
        print(f"  Created {len(nodes)} nodes")
        
        # Build edges from both similarity and citations
        edges = []
        edge_id = 0
        similarity_edges = 0
        citation_edges = 0
        
        # Add citation edges (stronger weight)
        for edge in citation_graph['edges']:
            source = edge['source']
            target = edge['target']
            
            if source in node_lookup and target in node_lookup:
                edges.append({
                    'id': f"cite_{edge_id}",
                    'source': source,
                    'target': target,
                    'type': 'citation',
                    'strength': 1.0,
                    'color': '#ef4444'  # Red for citations
                })
                edge_id += 1
                citation_edges += 1
        
        print(f"  Added {citation_edges} citation edges")
        
        # Add semantic similarity edges
        print(f"  Computing semantic similarity edges...")
        n = len(embeddings_data)
        
        for i in range(n):
            for j in range(i + 1, n):
                emb1 = embeddings_data[i]['embedding']
                emb2 = embeddings_data[j]['embedding']
                
                # Compute similarity
                similarity = self.embedding_service.compute_similarity(
                    json.dumps(emb1),
                    json.dumps(emb2)
                )
                
                if similarity >= similarity_threshold:
                    section1 = embeddings_data[i]['section'].section_number
                    section2 = embeddings_data[j]['section'].section_number
                    
                    # Determine color based on similarity strength
                    if similarity >= 0.95:
                        color = '#dc2626'  # Dark red - very strong
                    elif similarity >= 0.85:
                        color = '#f59e0b'  # Orange - strong
                    elif similarity >= 0.80:
                        color = '#3b82f6'  # Blue - moderate
                    else:
                        color = '#6b7280'  # Gray - weak
                    
                    edges.append({
                        'id': f"sim_{edge_id}",
                        'source': section1,
                        'target': section2,
                        'type': 'similarity',
                        'strength': round(similarity, 3),
                        'color': color
                    })
                    edge_id += 1
                    similarity_edges += 1
        
        print(f"  Added {similarity_edges} similarity edges")
        print(f"  Total edges: {len(edges)}")
        
        # Detect communities/clusters
        clusters = self._detect_communities(nodes, edges)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'clusters': clusters,
            'stats': {
                'total_nodes': len(nodes),
                'citation_edges': citation_edges,
                'similarity_edges': similarity_edges,
                'total_edges': len(edges),
                'avg_degree': len(edges) * 2 / len(nodes) if nodes else 0,
                'num_clusters': len(clusters)
            },
            'pagerank': pagerank_scores
        }
    
    def _detect_communities(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detect communities/clusters using simple connected components
        
        Args:
            nodes: List of node dictionaries
            edges: List of edge dictionaries
            
        Returns:
            List of cluster information
        """
        print("  Detecting communities...")
        
        # Build adjacency list
        adj = defaultdict(set)
        for edge in edges:
            adj[edge['source']].add(edge['target'])
            adj[edge['target']].add(edge['source'])
        
        # Find connected components
        visited = set()
        clusters = []
        cluster_id = 0
        
        node_ids = [n['id'] for n in nodes]
        
        for node_id in node_ids:
            if node_id not in visited:
                # BFS to find component
                component = []
                queue = [node_id]
                visited.add(node_id)
                
                while queue:
                    current = queue.pop(0)
                    component.append(current)
                    
                    for neighbor in adj[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                if len(component) >= 2:  # Only keep clusters with 2+ nodes
                    clusters.append({
                        'id': cluster_id,
                        'size': len(component),
                        'nodes': component
                    })
                    cluster_id += 1
        
        print(f"  Found {len(clusters)} communities")
        return clusters
    
    def get_network_statistics(self, network: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate detailed network statistics
        
        Args:
            network: Network graph data
            
        Returns:
            Dictionary with statistics
        """
        nodes = network['nodes']
        edges = network['edges']
        
        if not nodes:
            return {}
        
        # Degree distribution
        degree = defaultdict(int)
        for edge in edges:
            degree[edge['source']] += 1
            degree[edge['target']] += 1
        
        degrees = list(degree.values())
        
        # Find authorities (most cited)
        authorities = sorted(nodes, key=lambda x: x['citations_in'], reverse=True)[:10]
        
        # Find hubs (cite most)
        hubs = sorted(nodes, key=lambda x: x['citations_out'], reverse=True)[:10]
        
        # Find central nodes (highest PageRank)
        central = sorted(nodes, key=lambda x: x['pagerank'], reverse=True)[:10]
        
        return {
            'node_count': len(nodes),
            'edge_count': len(edges),
            'avg_degree': sum(degrees) / len(nodes) if nodes else 0,
            'max_degree': max(degrees) if degrees else 0,
            'min_degree': min(degrees) if degrees else 0,
            'density': len(edges) / (len(nodes) * (len(nodes) - 1) / 2) if len(nodes) > 1 else 0,
            'top_authorities': [
                {
                    'section': a['id'],
                    'subject': a['subject'],
                    'citations': a['citations_in'],
                    'pagerank': a['pagerank']
                }
                for a in authorities
            ],
            'top_hubs': [
                {
                    'section': h['id'],
                    'subject': h['subject'],
                    'citations': h['citations_out']
                }
                for h in hubs
            ],
            'top_central': [
                {
                    'section': c['id'],
                    'subject': c['subject'],
                    'pagerank': c['pagerank'],
                    'importance': c['importance']
                }
                for c in central
            ]
        }
    
    def find_shortest_path(self, network: Dict[str, Any], 
                          source: str, target: str) -> Optional[List[str]]:
        """
        Find shortest path between two sections
        
        Args:
            network: Network graph data
            source: Source section number
            target: Target section number
            
        Returns:
            List of section numbers forming path, or None if no path exists
        """
        edges = network['edges']
        
        # Build adjacency list
        adj = defaultdict(list)
        for edge in edges:
            adj[edge['source']].append(edge['target'])
            adj[edge['target']].append(edge['source'])
        
        # BFS for shortest path
        queue = [(source, [source])]
        visited = {source}
        
        while queue:
            current, path = queue.pop(0)
            
            if current == target:
                return path
            
            for neighbor in adj[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_ego_network(self, network: Dict[str, Any], 
                       center_node: str, radius: int = 1) -> Dict[str, Any]:
        """
        Extract ego network (subgraph centered on a node)
        
        Args:
            network: Full network graph data
            center_node: Center node section number
            radius: Number of hops to include
            
        Returns:
            Subgraph containing ego network
        """
        edges = network['edges']
        nodes = network['nodes']
        
        # Build adjacency list
        adj = defaultdict(set)
        for edge in edges:
            adj[edge['source']].add(edge['target'])
            adj[edge['target']].add(edge['source'])
        
        # BFS to find nodes within radius
        ego_nodes = {center_node}
        current_layer = {center_node}
        
        for _ in range(radius):
            next_layer = set()
            for node in current_layer:
                next_layer.update(adj[node])
            ego_nodes.update(next_layer)
            current_layer = next_layer
        
        # Filter nodes and edges
        filtered_nodes = [n for n in nodes if n['id'] in ego_nodes]
        filtered_edges = [
            e for e in edges 
            if e['source'] in ego_nodes and e['target'] in ego_nodes
        ]
        
        return {
            'nodes': filtered_nodes,
            'edges': filtered_edges,
            'center': center_node,
            'radius': radius,
            'stats': {
                'total_nodes': len(filtered_nodes),
                'total_edges': len(filtered_edges)
            }
        }


# Global instance
network_service = NetworkService()
