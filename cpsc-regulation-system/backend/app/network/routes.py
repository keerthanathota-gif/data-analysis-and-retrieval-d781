"""
Network Analysis Routes for CFR Regulations
API endpoints for semantic network graphs and citation analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.models.database import get_db
from app.auth.dependencies import require_auth
from app.services.network_service import network_service
from app.services.citation_service import citation_service

router = APIRouter(prefix="/network", tags=["Network Analysis"])


@router.post("/build")
async def build_semantic_network(
    similarity_threshold: float = Query(0.75, ge=0.0, le=1.0, description="Minimum similarity for edges"),
    max_sections: Optional[int] = Query(None, description="Limit sections for performance"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Build semantic network graph combining similarity and citations
    
    Returns network with nodes, edges, clusters, and statistics
    """
    try:
        network = network_service.build_semantic_network(
            db, 
            similarity_threshold=similarity_threshold,
            max_sections=max_sections
        )
        
        return {
            'success': True,
            'network': network
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build network: {str(e)}")


@router.get("/statistics")
async def get_network_statistics(
    similarity_threshold: float = Query(0.75, ge=0.0, le=1.0),
    max_sections: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Get detailed network statistics including authorities, hubs, and central nodes
    """
    try:
        # Build network
        network = network_service.build_semantic_network(
            db,
            similarity_threshold=similarity_threshold,
            max_sections=max_sections
        )
        
        # Calculate statistics
        stats = network_service.get_network_statistics(network)
        
        return {
            'success': True,
            'statistics': stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate statistics: {str(e)}")


@router.get("/citations")
async def get_citation_graph(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Get citation-only graph (which sections reference others)
    """
    try:
        citation_graph = citation_service.build_citation_graph(db)
        return {
            'success': True,
            'graph': citation_graph
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build citation graph: {str(e)}")


@router.get("/pagerank")
async def get_pagerank_scores(
    damping: float = Query(0.85, ge=0.0, le=1.0, description="PageRank damping factor"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Calculate PageRank scores for all sections
    """
    try:
        citation_graph = citation_service.build_citation_graph(db)
        pagerank = citation_service.calculate_pagerank(
            citation_graph,
            damping=damping
        )
        
        # Sort by score
        ranked = sorted(
            [{'section': k, 'score': v} for k, v in pagerank.items()],
            key=lambda x: x['score'],
            reverse=True
        )
        
        return {
            'success': True,
            'pagerank': ranked[:50],  # Top 50
            'total_sections': len(pagerank)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate PageRank: {str(e)}")


@router.get("/authorities")
async def get_top_authorities(
    top_k: int = Query(10, ge=1, le=100, description="Number of top authorities"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Get most cited sections (authority nodes)
    """
    try:
        citation_graph = citation_service.build_citation_graph(db)
        authorities = citation_service.find_most_cited_sections(citation_graph, top_k)
        
        return {
            'success': True,
            'authorities': authorities
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find authorities: {str(e)}")


@router.get("/hubs")
async def get_top_hubs(
    top_k: int = Query(10, ge=1, le=100, description="Number of top hubs"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Get sections that cite the most others (hub nodes)
    """
    try:
        citation_graph = citation_service.build_citation_graph(db)
        hubs = citation_service.find_hub_sections(citation_graph, top_k)
        
        return {
            'success': True,
            'hubs': hubs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find hubs: {str(e)}")


@router.get("/section/{section_number}/network")
async def get_section_network_info(
    section_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Get network information for a specific section
    """
    try:
        citation_graph = citation_service.build_citation_graph(db)
        network_info = citation_service.get_section_network_info(section_number, citation_graph)
        
        if not network_info:
            raise HTTPException(status_code=404, detail="Section not found")
        
        return {
            'success': True,
            'network_info': network_info
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get network info: {str(e)}")


@router.get("/ego/{center_node}")
async def get_ego_network(
    center_node: str,
    radius: int = Query(1, ge=1, le=3, description="Network radius (hops)"),
    similarity_threshold: float = Query(0.75, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Get ego network (subgraph) centered on a specific section
    """
    try:
        # Build full network
        network = network_service.build_semantic_network(
            db,
            similarity_threshold=similarity_threshold
        )
        
        # Extract ego network
        ego = network_service.get_ego_network(network, center_node, radius)
        
        return {
            'success': True,
            'ego_network': ego
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ego network: {str(e)}")


@router.get("/path/{source}/{target}")
async def find_shortest_path(
    source: str,
    target: str,
    similarity_threshold: float = Query(0.75, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_auth)
):
    """
    Find shortest path between two sections in the network
    """
    try:
        # Build network
        network = network_service.build_semantic_network(
            db,
            similarity_threshold=similarity_threshold
        )
        
        # Find path
        path = network_service.find_shortest_path(network, source, target)
        
        if path is None:
            return {
                'success': True,
                'path_found': False,
                'message': 'No path exists between these sections'
            }
        
        return {
            'success': True,
            'path_found': True,
            'path': path,
            'length': len(path) - 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find path: {str(e)}")
