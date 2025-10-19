"""
Search routes for CPSC Regulation System
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.models.auth_database import get_auth_db
from app.models.cfr_database import get_cfr_db
from app.models.schemas import SearchRequest, SearchResponse
from app.auth.dependencies import get_current_active_user
from app.auth.auth_service import AuthService
from app.services.rag_service import RAGService

router = APIRouter(prefix="/search", tags=["search"])
auth_service = AuthService()
rag_service = RAGService()

@router.post("/query", response_model=SearchResponse)
async def search_regulations(
    request: SearchRequest,
    current_user = Depends(get_current_active_user),
    request_client: Request = None,
    auth_db: Session = Depends(get_auth_db),
    cfr_db: Session = Depends(get_cfr_db)
):
    """Search regulations using semantic search"""
    try:
        # Perform search
        results = rag_service.query_database(
            request.query,
            request.level,
            cfr_db,
            top_k=request.top_k
        )

        # Get context for RAG
        context = rag_service.get_context_for_query(request.query, cfr_db)

        # Log activity
        auth_service.log_activity(
            db=auth_db,
            user_id=current_user.id,
            action="search",
            details=f"User {current_user.username} searched for: {request.query[:100]}..."
        )
        
        return SearchResponse(
            query=request.query,
            level=request.level,
            top_k=request.top_k,
            results=results,
            total_results=len(results)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing search: {str(e)}"
        )

@router.get("/similar/{name}")
async def find_similar_sections(
    name: str,
    search_type: str = "section",
    top_k: int = 20,
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db),
    cfr_db: Session = Depends(get_cfr_db)
):
    """Find similar sections by name"""
    try:
        results = rag_service.find_similar_by_name(
            name,
            search_type,
            cfr_db,
            top_k=top_k
        )

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No similar items found or item not found"
            )

        # Log activity
        auth_service.log_activity(
            db=auth_db,
            user_id=current_user.id,
            action="similarity_search",
            details=f"User {current_user.username} searched for similar items to: {name}"
        )
        
        return {
            "search_name": name,
            "search_type": search_type,
            "top_k": top_k,
            "results": results,
            "total_results": len(results)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding similar sections: {str(e)}"
        )

@router.get("/section/{section_id}")
async def get_section_details(
    section_id: int,
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db),
    cfr_db: Session = Depends(get_cfr_db)
):
    """Get full details of a specific section"""
    try:
        from app.models.cfr_database import Section

        section = cfr_db.query(Section).filter(Section.id == section_id).first()
        
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found"
            )
        
        # Get hierarchy
        part = section.part
        subchapter = part.subchapter if part else None
        chapter = subchapter.chapter if subchapter else None
        
        # Log activity
        auth_service.log_activity(
            db=auth_db,
            user_id=current_user.id,
            action="section_view",
            details=f"User {current_user.username} viewed section {section.section_number}"
        )
        
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting section details: {str(e)}"
        )

@router.get("/sections")
async def get_sections_list(
    skip: int = 0,
    limit: int = 50,
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db),
    cfr_db: Session = Depends(get_cfr_db)
):
    """Get list of sections with pagination"""
    try:
        from app.models.cfr_database import Section

        sections = cfr_db.query(Section).offset(skip).limit(limit).all()
        total_count = cfr_db.query(Section).count()

        # Log activity
        auth_service.log_activity(
            db=auth_db,
            user_id=current_user.id,
            action="sections_list",
            details=f"User {current_user.username} viewed sections list"
        )
        
        return {
            "sections": [
                {
                    "id": section.id,
                    "section_number": section.section_number,
                    "subject": section.subject,
                    "citation": section.citation
                }
                for section in sections
            ],
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting sections list: {str(e)}"
        )