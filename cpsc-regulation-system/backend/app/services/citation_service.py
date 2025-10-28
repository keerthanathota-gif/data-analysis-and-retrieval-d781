"""
Citation Extraction Service for CFR Regulations
Extracts and analyzes cross-references between regulations
"""

import re
from typing import List, Dict, Any, Set, Tuple
from sqlalchemy.orm import Session
from collections import defaultdict

from app.models.database import Section


class CitationService:
    """Service for extracting and analyzing citations between regulations"""
    
    def __init__(self):
        """Initialize citation patterns for CFR references"""
        # Common CFR citation patterns
        self.citation_patterns = [
            # § 1234.56 or §1234.56
            r'§\s*(\d+)\.(\d+)',
            # Section 1234.56
            r'[Ss]ection\s+(\d+)\.(\d+)',
            # 16 CFR 1234.56
            r'\d+\s+CFR\s+(\d+)\.(\d+)',
            # part 1234
            r'[Pp]art\s+(\d+)',
            # subpart 1234
            r'[Ss]ubpart\s+([A-Z])',
        ]
        
        self.compiled_patterns = [re.compile(pattern) for pattern in self.citation_patterns]
    
    def extract_citations(self, text: str) -> List[str]:
        """
        Extract all CFR citations from text
        
        Args:
            text: Text to extract citations from
            
        Returns:
            List of cited section numbers
        """
        if not text:
            return []
        
        citations = set()
        
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            for match in matches:
                if isinstance(match, tuple):
                    # For patterns that capture section numbers
                    if len(match) == 2:
                        citation = f"{match[0]}.{match[1]}"
                        citations.add(citation)
                else:
                    citations.add(match)
        
        return list(citations)
    
    def build_citation_graph(self, db: Session) -> Dict[str, Any]:
        """
        Build complete citation graph for all sections
        
        Args:
            db: Database session
            
        Returns:
            Dictionary containing nodes, edges, and analysis
        """
        print("Building citation graph...")
        
        # Get all sections
        sections = db.query(Section).all()
        print(f"  Analyzing {len(sections)} sections")
        
        # Build citation map
        citation_map = defaultdict(list)  # source -> [targets]
        section_lookup = {}  # section_number -> section
        
        for section in sections:
            section_lookup[section.section_number] = section
            
            if section.text:
                citations = self.extract_citations(section.text)
                if citations:
                    citation_map[section.section_number] = citations
        
        print(f"  Found {len(citation_map)} sections with citations")
        
        # Build nodes and edges
        nodes = []
        edges = []
        cited_by = defaultdict(int)  # How many times each section is cited
        cites = defaultdict(int)  # How many sections each section cites
        
        for section in sections:
            # Count incoming citations
            for source, targets in citation_map.items():
                if section.section_number in targets:
                    cited_by[section.section_number] += 1
            
            # Count outgoing citations
            if section.section_number in citation_map:
                cites[section.section_number] = len(citation_map[section.section_number])
            
            # Create node
            node = {
                'id': section.section_number,
                'label': section.section_number,
                'subject': section.subject or 'No subject',
                'citation': section.citation or '',
                'text_length': len(section.text) if section.text else 0,
                'citations_out': cites[section.section_number],
                'citations_in': cited_by[section.section_number],
                'importance': cited_by[section.section_number] + cites[section.section_number] * 0.5
            }
            nodes.append(node)
        
        # Create edges
        edge_id = 0
        for source_number, target_numbers in citation_map.items():
            for target_number in target_numbers:
                # Only create edge if target exists in our database
                if target_number in section_lookup:
                    edges.append({
                        'id': f"edge_{edge_id}",
                        'source': source_number,
                        'target': target_number,
                        'type': 'citation'
                    })
                    edge_id += 1
        
        print(f"  Created {len(nodes)} nodes and {len(edges)} citation edges")
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_sections': len(sections),
                'sections_with_citations': len(citation_map),
                'total_citations': len(edges),
                'avg_citations_per_section': len(edges) / len(sections) if sections else 0
            }
        }
    
    def find_most_cited_sections(self, citation_graph: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Find the most cited sections (authority nodes)
        
        Args:
            citation_graph: Graph data from build_citation_graph
            top_k: Number of top sections to return
            
        Returns:
            List of most cited sections
        """
        nodes = citation_graph['nodes']
        
        # Sort by incoming citations
        sorted_nodes = sorted(nodes, key=lambda x: x['citations_in'], reverse=True)
        
        return sorted_nodes[:top_k]
    
    def find_hub_sections(self, citation_graph: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Find hub sections (sections that cite many others)
        
        Args:
            citation_graph: Graph data from build_citation_graph
            top_k: Number of top hubs to return
            
        Returns:
            List of hub sections
        """
        nodes = citation_graph['nodes']
        
        # Sort by outgoing citations
        sorted_nodes = sorted(nodes, key=lambda x: x['citations_out'], reverse=True)
        
        return sorted_nodes[:top_k]
    
    def calculate_pagerank(self, citation_graph: Dict[str, Any], 
                          damping: float = 0.85, 
                          max_iter: int = 100,
                          tol: float = 1e-6) -> Dict[str, float]:
        """
        Calculate PageRank scores for all sections
        
        Args:
            citation_graph: Graph data from build_citation_graph
            damping: Damping factor (default 0.85)
            max_iter: Maximum iterations
            tol: Convergence tolerance
            
        Returns:
            Dictionary mapping section_number to PageRank score
        """
        print("Calculating PageRank scores...")
        
        nodes = citation_graph['nodes']
        edges = citation_graph['edges']
        
        if not nodes:
            return {}
        
        # Create adjacency structure
        node_ids = [node['id'] for node in nodes]
        n = len(node_ids)
        node_index = {node_id: i for i, node_id in enumerate(node_ids)}
        
        # Initialize PageRank scores
        pagerank = {node_id: 1.0 / n for node_id in node_ids}
        
        # Build outgoing links map
        outgoing = defaultdict(list)
        for edge in edges:
            source = edge['source']
            target = edge['target']
            if source in node_index and target in node_index:
                outgoing[source].append(target)
        
        # Iterative PageRank calculation
        for iteration in range(max_iter):
            new_pagerank = {}
            max_change = 0
            
            for node_id in node_ids:
                # Calculate rank from incoming links
                rank_sum = 0
                for other_id in node_ids:
                    if node_id in outgoing[other_id]:
                        num_outgoing = len(outgoing[other_id])
                        if num_outgoing > 0:
                            rank_sum += pagerank[other_id] / num_outgoing
                
                # Apply damping factor
                new_rank = (1 - damping) / n + damping * rank_sum
                new_pagerank[node_id] = new_rank
                
                # Track convergence
                change = abs(new_rank - pagerank[node_id])
                max_change = max(max_change, change)
            
            pagerank = new_pagerank
            
            # Check convergence
            if max_change < tol:
                print(f"  Converged after {iteration + 1} iterations")
                break
        
        print(f"  PageRank calculation complete")
        return pagerank
    
    def get_section_network_info(self, section_number: str, 
                                 citation_graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed network information for a specific section
        
        Args:
            section_number: Section number to analyze
            citation_graph: Graph data from build_citation_graph
            
        Returns:
            Dictionary with section's network information
        """
        # Find the node
        node = next((n for n in citation_graph['nodes'] if n['id'] == section_number), None)
        if not node:
            return None
        
        # Find all edges involving this section
        edges = citation_graph['edges']
        outgoing = [e for e in edges if e['source'] == section_number]
        incoming = [e for e in edges if e['target'] == section_number]
        
        return {
            'section_number': section_number,
            'subject': node['subject'],
            'citations_made': len(outgoing),
            'citations_received': len(incoming),
            'importance_score': node['importance'],
            'cites': [e['target'] for e in outgoing],
            'cited_by': [e['source'] for e in incoming]
        }


# Global instance
citation_service = CitationService()
