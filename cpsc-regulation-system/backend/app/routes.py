"""
API Routes for PDF Report Generation
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.services.pdf_report_service import pdf_report_service

router = APIRouter(prefix="/api/reports", tags=["Reports"])


class ReportRequest(BaseModel):
    """Request model for PDF report generation"""
    level: str
    total_items: int
    total_relationships: int
    health_score: dict
    categorized_relationships: dict
    insights: Optional[dict] = None


@router.post("/generate-analysis-pdf")
async def generate_analysis_pdf(request: ReportRequest):
    """
    Generate PDF report from analysis data

    Args:
        request: Analysis data including redundancy, parity, and overlap

    Returns:
        PDF file as streaming response
    """
    try:
        # Convert request to dict
        analysis_data = request.dict()

        # Generate PDF
        pdf_buffer = pdf_report_service.generate_analysis_report(analysis_data)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"CFR_Analysis_Report_{request.level}_{timestamp}.pdf"

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )
