"""
Main FastAPI Application for CFR Agentic AI Application
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import os
import json

from app.database import get_db, init_db, reset_db, SessionLocal, Section, SimilarityResult, ParityCheck
from app.pipeline.data_pipeline import DataPipeline
from app.services.analysis_service import AnalysisService
from app.services.clustering_service import ClusteringService
from app.services.rag_service import RAGService
from app.services.visualization_service import VisualizationService
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import get_llm_service
from app.config import API_HOST, API_PORT, VISUALIZATIONS_DIR, DATA_DIR, OUTPUT_DIR

# Initialize FastAPI app
app = FastAPI(
    title="CFR Agentic AI Application",
    description="Intelligent analysis and retrieval system for Code of Federal Regulations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount static files for visualizations
app.mount("/visualizations", StaticFiles(directory=VISUALIZATIONS_DIR), name="visualizations")

# Initialize service instances
analysis_service = AnalysisService()
clustering_service = ClusteringService()
rag_service = RAGService()
visualization_service = VisualizationService()
embedding_service = EmbeddingService()

# Global pipeline instance and status tracking
pipeline_instance = None
pipeline_status_global = {
    'state': 'idle',
    'current_step': None,
    'progress': 0,
    'total_steps': 6,
    'steps_completed': [],
    'error_message': None,
    'start_time': None,
    'end_time': None,
    'stats': {}
}

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized")


# Pydantic models for request/response
class PipelineRequest(BaseModel):
    urls: List[str]  # List of URLs to crawl


class AnalysisRequest(BaseModel):
    level: str  # 'chapter', 'subchapter', 'section'
    check_similarity: bool = True
    check_overlap: bool = True
    check_redundancy: bool = True
    check_parity: bool = True


class ClusteringRequest(BaseModel):
    level: str
    n_clusters: Optional[int] = None  # Number of clusters for K-Means


class QueryRequest(BaseModel):
    query: str
    level: str = "all"  # 'chapter', 'subchapter', 'section', 'all'
    top_k: Optional[int] = 10


class SimilaritySearchRequest(BaseModel):
    name: str
    search_type: str  # 'chapter', 'subchapter', 'section'
    top_k: Optional[int] = 10


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "CFR Agentic AI Application",
        "version": "1.0.0",
        "status": "running"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Data Pipeline Endpoints
@app.post("/api/pipeline/run")
async def run_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """
    Run the complete data pipeline in the background with user-provided URLs
    
    Args:
        request: Contains list of CFR URLs to process
    """
    global pipeline_instance, pipeline_status_global
    
    def run_pipeline_task():
        global pipeline_instance, pipeline_status_global
        try:
            pipeline_instance = DataPipeline(urls=request.urls)
            pipeline_instance.run_full_pipeline()
            # Update global status
            pipeline_status_global = pipeline_instance.get_status()
        except Exception as e:
            pipeline_status_global = {
                'state': 'error',
                'error_message': str(e),
                'progress': 0,
                'current_step': 'Error',
                'stats': {}
            }
    
    background_tasks.add_task(run_pipeline_task)
    
    # Reset status to running
    pipeline_status_global = {
        'state': 'running',
        'current_step': 'Starting',
        'progress': 0,
        'total_steps': 6,
        'steps_completed': [],
        'error_message': None,
        'start_time': None,
        'end_time': None,
        'stats': {}
    }
    
    return {
        "message": "Pipeline started in background",
        "status": "processing",
        "urls": request.urls,
        "num_urls": len(request.urls)
    }


@app.get("/api/pipeline/stats")
async def get_pipeline_stats():
    """Get statistics about the stored data"""
    pipeline = DataPipeline()
    stats = pipeline.get_statistics()
    return stats


@app.get("/api/pipeline/status")
async def get_pipeline_status():
    """Get current pipeline status"""
    global pipeline_instance, pipeline_status_global
    
    # If pipeline instance exists, get live status
    if pipeline_instance:
        return pipeline_instance.get_status()
    
    # Otherwise return global status
    return pipeline_status_global


@app.post("/api/pipeline/reset")
async def reset_pipeline():
    """Reset entire database and clear all data"""
    try:
        import shutil
        from config import DATA_DIR, OUTPUT_DIR, VISUALIZATIONS_DIR
        
        # Reset database
        reset_db()
        
        # Clear data directories
        for directory in [DATA_DIR, OUTPUT_DIR, VISUALIZATIONS_DIR]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
                os.makedirs(directory)
        
        return {
            "message": "Database and data reset successfully",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


# Analysis Endpoints
@app.post("/api/analysis/similarity")
async def analyze_similarity(request: AnalysisRequest, db: Session = Depends(get_db)):
    """Analyze semantic similarity at specified level"""
    try:
        results = analysis_service.analyze_semantic_similarity(request.level, db)
        return {
            "level": request.level,
            "total_pairs": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/overlaps/{level}")
async def get_overlaps(level: str, db: Session = Depends(get_db)):
    """Get overlapping items at specified level"""
    try:
        overlaps = analysis_service.check_overlaps(level, db)
        return {
            "level": level,
            "total_overlaps": len(overlaps),
            "results": overlaps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/redundancy/{level}")
async def get_redundancy(level: str, db: Session = Depends(get_db)):
    """Get redundant items at specified level"""
    try:
        redundancies = analysis_service.check_redundancy(level, db)
        return {
            "level": level,
            "total_redundancies": len(redundancies),
            "results": redundancies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analysis/parity")
async def perform_parity_check(request: AnalysisRequest, db: Session = Depends(get_db)):
    """Perform parity checks at specified level"""
    try:
        results = analysis_service.perform_parity_check(request.level, db)
        return {
            "level": request.level,
            "total_checks": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/summary/{level}")
async def get_analysis_summary(level: str, db: Session = Depends(get_db)):
    """Get a summary of all analyses for a given level"""
    try:
        summary = analysis_service.get_analysis_summary(level, db)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/details/{result_id}")
async def get_analysis_details(result_id: int, db: Session = Depends(get_db)):
    """Get detailed analysis including LLM justification for a specific result"""
    try:
        # Get similarity result
        sim_result = db.query(SimilarityResult).filter(SimilarityResult.id == result_id).first()
        
        if not sim_result:
            raise HTTPException(status_code=404, detail="Analysis result not found")
        
        # Get item details
        from database import Chapter, Subchapter, Section
        
        if sim_result.item1_type == 'chapter':
            item1 = db.query(Chapter).filter(Chapter.id == sim_result.item1_id).first()
            item2 = db.query(Chapter).filter(Chapter.id == sim_result.item2_id).first()
            item1_name = item1.name if item1 else "Unknown"
            item2_name = item2.name if item2 else "Unknown"
        elif sim_result.item1_type == 'subchapter':
            item1 = db.query(Subchapter).filter(Subchapter.id == sim_result.item1_id).first()
            item2 = db.query(Subchapter).filter(Subchapter.id == sim_result.item2_id).first()
            item1_name = item1.name if item1 else "Unknown"
            item2_name = item2.name if item2 else "Unknown"
        else:  # section
            item1 = db.query(Section).filter(Section.id == sim_result.item1_id).first()
            item2 = db.query(Section).filter(Section.id == sim_result.item2_id).first()
            item1_name = f"{item1.section_number}: {item1.subject}" if item1 else "Unknown"
            item2_name = f"{item2.section_number}: {item2.subject}" if item2 else "Unknown"
        
        # Generate LLM justification if not exists
        if not sim_result.llm_justification:
            llm = get_llm_service()
            
            # Generate overlap explanation
            overlap_explanation = llm.generate_overlap_explanation(
                item1_name, item2_name, sim_result.similarity_score
            )
            
            # Generate redundancy justification if redundant
            if sim_result.is_redundant:
                redundancy_justification = llm.generate_redundancy_justification(
                    item1_name, item2_name, sim_result.similarity_score, True
                )
            else:
                redundancy_justification = None
            
            # Combine justifications
            justification = overlap_explanation
            if redundancy_justification:
                justification += "\n\nRedundancy Analysis: " + redundancy_justification
            
            # Update database
            sim_result.llm_justification = justification
            db.commit()
        
        return {
            "id": sim_result.id,
            "item1_type": sim_result.item1_type,
            "item1_id": sim_result.item1_id,
            "item1_name": item1_name,
            "item2_id": sim_result.item2_id,
            "item2_name": item2_name,
            "similarity_score": sim_result.similarity_score,
            "is_overlap": sim_result.is_overlap,
            "is_redundant": sim_result.is_redundant,
            "overlap_data": sim_result.overlap_data,
            "llm_justification": sim_result.llm_justification
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Clustering Endpoints
@app.post("/api/clustering/cluster")
async def cluster_items(request: ClusteringRequest, db: Session = Depends(get_db)):
    """
    Perform K-Means clustering at specified level
    For chapters/subchapters, clusters based on aggregated section embeddings
    """
    try:
        results = clustering_service.cluster_items(
            request.level,
            db,
            n_clusters=request.n_clusters
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clustering/clusters/{level}")
async def get_clusters(level: str, db: Session = Depends(get_db)):
    """Get all clusters for a specific level"""
    try:
        clusters = clustering_service.get_all_clusters(level, db)
        return {
            "level": level,
            "total_clusters": len(clusters),
            "clusters": clusters
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clustering/cluster/{cluster_id}")
async def get_cluster_details(cluster_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific cluster"""
    try:
        cluster = clustering_service.get_cluster_by_id(cluster_id, db)
        if not cluster:
            raise HTTPException(status_code=404, detail="Cluster not found")
        return cluster
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# RAG Endpoints
@app.post("/api/rag/query")
async def query_database(request: QueryRequest, db: Session = Depends(get_db)):
    """Query the database using semantic search"""
    try:
        results = rag_service.query_database(
            request.query,
            request.level,
            db,
            top_k=request.top_k
        )
        
        # Get context for RAG
        context = rag_service.get_context_for_query(request.query, db)
        
        return {
            "query": request.query,
            "level": request.level,
            "top_k": request.top_k,
            "results": results,
            "context": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/rag/similar")
async def find_similar(request: SimilaritySearchRequest, db: Session = Depends(get_db)):
    """Find similar items by name"""
    try:
        results = rag_service.find_similar_by_name(
            request.name,
            request.search_type,
            db,
            top_k=request.top_k
        )
        
        if not results:
            raise HTTPException(status_code=404, detail="No similar items found or item not found")
        
        return {
            "search_name": request.name,
            "search_type": request.search_type,
            "top_k": request.top_k,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/section/{section_id}")
async def get_section_details(section_id: int, db: Session = Depends(get_db)):
    """Get full details of a specific section"""
    try:
        section = db.query(Section).filter(Section.id == section_id).first()
        
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
        
        # Get hierarchy
        part = section.part
        subchapter = part.subchapter if part else None
        chapter = subchapter.chapter if subchapter else None
        
        return {
            "id": section.id,
            "section_number": section.section_number,
            "subject": section.subject,
            "text": section.text,
            "citation": section.citation,
            "section_label": section.section_label,
            "part_heading": part.heading if part else None,
            "subchapter_name": subchapter.name if subchapter else None,
            "chapter_name": chapter.name if chapter else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Visualization Endpoints
@app.post("/api/visualization/clusters")
async def visualize_clusters(request: ClusteringRequest, db: Session = Depends(get_db)):
    """Generate cluster visualizations using K-Means"""
    try:
        # First perform clustering
        clustering_result = clustering_service.cluster_items(
            request.level,
            db,
            n_clusters=request.n_clusters
        )
        
        if clustering_result['num_clusters'] == 0:
            return {"message": "No clusters to visualize"}
        
        # Get embeddings and labels
        from database import Chapter, Subchapter, Section, ChapterEmbedding, SubchapterEmbedding, SectionEmbedding
        
        embeddings = []
        labels = []
        items = []
        
        for cluster in clustering_result['clusters']:
            for item in cluster['items']:
                items.append(item)
                labels.append(cluster['label'])
                
                # Get embedding based on type
                if request.level == 'chapter':
                    emb = db.query(ChapterEmbedding).filter(
                        ChapterEmbedding.chapter_id == item['id']
                    ).first()
                elif request.level == 'subchapter':
                    emb = db.query(SubchapterEmbedding).filter(
                        SubchapterEmbedding.subchapter_id == item['id']
                    ).first()
                elif request.level == 'section':
                    emb = db.query(SectionEmbedding).filter(
                        SectionEmbedding.section_id == item['id']
                    ).first()
                
                if emb:
                    embeddings.append(json.loads(emb.embedding))
        
        # Generate visualizations
        vis_files = {}
        
        # 2D visualization (t-SNE)
        tsne_path = visualization_service.visualize_clusters_2d(
            clustering_result['clusters'],
            embeddings,
            labels,
            request.level,
            method='tsne'
        )
        vis_files['tsne_2d'] = f"/visualizations/{os.path.basename(tsne_path)}"
        
        # 2D visualization (PCA)
        pca_path = visualization_service.visualize_clusters_2d(
            clustering_result['clusters'],
            embeddings,
            labels,
            request.level,
            method='pca'
        )
        vis_files['pca_2d'] = f"/visualizations/{os.path.basename(pca_path)}"
        
        # Interactive 3D visualization
        interactive_path = visualization_service.visualize_clusters_interactive(
            clustering_result['clusters'],
            embeddings,
            labels,
            items,
            request.level
        )
        vis_files['interactive_3d'] = f"/visualizations/{os.path.basename(interactive_path)}"
        
        # Cluster sizes
        sizes_path = visualization_service.visualize_cluster_sizes(
            clustering_result['clusters'],
            request.level
        )
        vis_files['cluster_sizes'] = f"/visualizations/{os.path.basename(sizes_path)}"
        
        # Cluster report
        report_path = visualization_service.create_cluster_report(
            clustering_result['clusters'],
            request.level
        )
        vis_files['cluster_report'] = f"/visualizations/{os.path.basename(report_path)}"
        
        return {
            "level": request.level,
            "algorithm": "kmeans",
            "num_clusters": clustering_result['num_clusters'],
            "visualizations": vis_files,
            "clustering_result": clustering_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# MCP (Model Context Protocol) Endpoints
@app.get("/mcp/tools")
async def mcp_list_tools():
    """List available tools for Model Context Protocol"""
    return {
        "tools": [
            {
                "name": "analyze_similarity",
                "description": "Analyze semantic similarity between CFR items",
                "parameters": {
                    "level": {
                        "type": "string",
                        "enum": ["chapter", "subchapter", "section"],
                        "required": True
                    }
                }
            },
            {
                "name": "cluster_items",
                "description": "Cluster CFR items automatically using K-Means",
                "parameters": {
                    "level": {
                        "type": "string",
                        "enum": ["chapter", "subchapter", "section"],
                        "required": True
                    },
                    "n_clusters": {
                        "type": "integer",
                        "required": False,
                        "description": "Number of clusters (auto-calculated if not provided)"
                    }
                }
            },
            {
                "name": "query_database",
                "description": "Query the CFR database using semantic search",
                "parameters": {
                    "query": {
                        "type": "string",
                        "required": True
                    },
                    "level": {
                        "type": "string",
                        "enum": ["chapter", "subchapter", "section", "all"],
                        "required": False
                    }
                }
            },
            {
                "name": "find_similar",
                "description": "Find similar CFR items by name",
                "parameters": {
                    "name": {
                        "type": "string",
                        "required": True
                    },
                    "search_type": {
                        "type": "string",
                        "enum": ["chapter", "subchapter", "section"],
                        "required": True
                    }
                }
            }
        ]
    }


@app.post("/mcp/execute")
async def mcp_execute_tool(tool_name: str, parameters: Dict[str, Any], db: Session = Depends(get_db)):
    """Execute a tool via Model Context Protocol"""
    try:
        if tool_name == "analyze_similarity":
            results = analysis_service.analyze_semantic_similarity(parameters['level'], db)
            return {"status": "success", "results": results}
        
        elif tool_name == "cluster_items":
            results = clustering_service.cluster_items(
                parameters['level'],
                db,
                n_clusters=parameters.get('n_clusters')
            )
            return {"status": "success", "results": results}
        
        elif tool_name == "query_database":
            results = rag_service.query_database(
                parameters['query'],
                parameters.get('level', 'all'),
                db
            )
            return {"status": "success", "results": results}
        
        elif tool_name == "find_similar":
            results = rag_service.find_similar_by_name(
                parameters['name'],
                parameters['search_type'],
                db
            )
            return {"status": "success", "results": results}
        
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve the UI
@app.get("/ui")
async def serve_ui():
    """Serve the UI"""
    import os
    static_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(static_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
