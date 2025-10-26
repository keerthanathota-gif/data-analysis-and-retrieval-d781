"""
Admin routes for CPSC Regulation System
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List
from app.models.auth_database import get_auth_db, UserRole
from app.models.cfr_database import get_cfr_db, Section, Chapter, Subchapter
from app.models.schemas import (
    UserResponse, UserManagementRequest, AdminStats,
    PipelineRequest, PipelineResponse, PipelineStatus,
    ActivityLogResponse
)
from app.auth.dependencies import get_current_active_user
from app.auth.auth_service import AuthService
from app.pipeline.data_pipeline import DataPipeline
from app.services.analysis_service import AnalysisService
from app.services.clustering_service import ClusteringService

router = APIRouter(prefix="/admin", tags=["admin"])
auth_service = AuthService()
analysis_service = AnalysisService()
clustering_service = ClusteringService()

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

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db),
    cfr_db: Session = Depends(get_cfr_db)
):
    """Get system statistics"""
    try:
        user_stats = auth_service.get_user_stats(auth_db)

        # Get data statistics
        total_sections = cfr_db.query(Section).count()
        total_chapters = cfr_db.query(Chapter).count()
        total_subchapters = cfr_db.query(Subchapter).count()

        return AdminStats(
            total_users=user_stats["total_users"],
            active_users=user_stats["active_users"],
            inactive_users=user_stats["inactive_users"],
            admin_users=user_stats["admin_users"],
            regular_users=user_stats["regular_users"],
            total_sections=total_sections,
            total_chapters=total_chapters,
            total_subchapters=total_subchapters
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}"
        )

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db)
):
    """Get all users with pagination"""
    try:
        users = auth_service.get_all_users(auth_db, skip=skip, limit=limit)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting users: {str(e)}"
        )

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db)
):
    """Update user role"""
    try:
        user = auth_service.update_user_role(auth_db, user_id, new_role)

        # Log activity
        auth_service.log_activity(
            db=auth_db,
            user_id=current_user.id,
            action="user_role_update",
            details=f"Admin {current_user.username} changed user {user.username} role to {new_role.value}"
        )

        return {"message": f"User role updated to {new_role.value}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user role: {str(e)}"
        )

@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db)
):
    """Activate user"""
    try:
        user = auth_service.activate_user(auth_db, user_id)

        # Log activity
        auth_service.log_activity(
            db=auth_db,
            user_id=current_user.id,
            action="user_activate",
            details=f"Admin {current_user.username} activated user {user.username}"
        )

        return {"message": "User activated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activating user: {str(e)}"
        )

@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db)
):
    """Deactivate user"""
    try:
        user = auth_service.deactivate_user(auth_db, user_id)

        # Log activity
        auth_service.log_activity(
            db=auth_db,
            user_id=current_user.id,
            action="user_deactivate",
            details=f"Admin {current_user.username} deactivated user {user.username}"
        )

        return {"message": "User deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating user: {str(e)}"
        )

@router.get("/activity-logs", response_model=List[ActivityLogResponse])
async def get_activity_logs(
    user_id: int = None,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db)
):
    """Get activity logs with optional user filter"""
    try:
        logs = auth_service.get_activity_logs(auth_db, user_id=user_id, skip=skip, limit=limit)
        return logs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting activity logs: {str(e)}"
        )

@router.post("/pipeline/run", response_model=PipelineResponse)
async def run_pipeline(
    request: PipelineRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db)
):
    """Run the complete data pipeline"""
    global pipeline_instance, pipeline_status_global
    
    def run_pipeline_task():
        global pipeline_instance, pipeline_status_global
        try:
            pipeline_instance = DataPipeline(urls=request.urls)
            pipeline_instance.run_full_pipeline()
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
    
    # Log activity
    auth_service.log_activity(
        db=auth_db,
        user_id=current_user.id,
        action="pipeline_run",
        details=f"Admin {current_user.username} started pipeline with {len(request.urls)} URLs"
    )
    
    return PipelineResponse(
        message="Pipeline started in background",
        status="processing",
        urls=request.urls,
        num_urls=len(request.urls)
    )

@router.get("/pipeline/status", response_model=PipelineStatus)
async def get_pipeline_status(
    current_user = Depends(get_current_active_user)
):
    """Get current pipeline status"""
    global pipeline_instance, pipeline_status_global
    
    if pipeline_instance:
        return pipeline_instance.get_status()
    
    return pipeline_status_global

@router.post("/pipeline/reset")
async def reset_pipeline(
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db),
    cfr_db: Session = Depends(get_cfr_db)
):
    """Reset entire database and clear all data"""
    try:
        import shutil
        from app.config import DATA_DIR, OUTPUT_DIR, VISUALIZATIONS_DIR
        import os
        import time

        # Reset CFR database only
        from app.models.cfr_database import reset_cfr_db
        reset_cfr_db()

        # Clear data directories with proper error handling
        for directory in [DATA_DIR, OUTPUT_DIR, VISUALIZATIONS_DIR]:
            try:
                if os.path.exists(directory):
                    # Use ignore_errors to handle any file locking issues
                    shutil.rmtree(directory, ignore_errors=True)
                    # Small delay to ensure filesystem sync
                    time.sleep(0.1)
                
                # Recreate the directory with exist_ok=True for safety
                os.makedirs(directory, exist_ok=True)
                
                # Verify directory is writable
                if not os.access(directory, os.W_OK):
                    raise PermissionError(f"Directory {directory} is not writable after recreation")
                    
                print(f"Reset and recreated directory: {directory}")
            except Exception as e:
                print(f"Warning: Error handling directory {directory}: {e}")
                # Try to ensure directory exists even if deletion failed
                os.makedirs(directory, exist_ok=True)

        # Log activity
        auth_service.log_activity(
            db=auth_db,
            user_id=current_user.id,
            action="pipeline_reset",
            details=f"Admin {current_user.username} reset the entire pipeline"
        )

        return {
            "message": "CFR database and data reset successfully",
            "status": "success"
        }
    except Exception as e:
        import traceback
        error_details = f"{type(e).__name__}: {str(e)}"
        print(f"Reset error: {error_details}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reset failed: {error_details}"
        )

@router.post("/analysis/run")
async def run_analysis(
    level: str,
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db),
    cfr_db: Session = Depends(get_cfr_db)
):
    """Run analysis on specified level"""
    try:
        results = analysis_service.analyze_semantic_similarity(level, cfr_db)

        # Log activity
        auth_service.log_activity(
            db=auth_db,
            user_id=current_user.id,
            action="analysis_run",
            details=f"Admin {current_user.username} ran analysis on {level} level"
        )

        return {
            "level": level,
            "total_pairs": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running analysis: {str(e)}"
        )

@router.post("/clustering/run")
async def run_clustering(
    level: str,
    n_clusters: int = None,
    current_user = Depends(get_current_active_user),
    auth_db: Session = Depends(get_auth_db),
    cfr_db: Session = Depends(get_cfr_db)
):
    """Run clustering on specified level"""
    try:
        results = clustering_service.cluster_items(level, cfr_db, n_clusters=n_clusters)

        # Log activity
        auth_service.log_activity(
            db=auth_db,
            user_id=current_user.id,
            action="clustering_run",
            details=f"Admin {current_user.username} ran clustering on {level} level"
        )

        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running clustering: {str(e)}"
        )