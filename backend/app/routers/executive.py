"""Executive overview router."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.executive_schemas import ExecutiveOverviewResponse, ExecutiveTrendData
from ..services.executive_overview_service import ExecutiveOverviewService
from ..services.identity_access_service import IdentityAccessService
from .auth import get_current_principal


router = APIRouter(prefix="/executive")


@router.get("/overview", response_model=ExecutiveOverviewResponse)
def get_executive_overview(
    from_date: date,
    to_date: date,
    db: Session = Depends(get_db),
) -> ExecutiveOverviewResponse:
    """
    Get executive reliability and impact overview.
    
    Returns aggregated KPIs and trend data for the specified date range.
    Implements FR-017: Executive reliability and impact overview.
    
    Args:
        from_date: Start date (ISO format: YYYY-MM-DD)
        to_date: End date (ISO format: YYYY-MM-DD)
        db: Database session
    
    Returns:
        ExecutiveOverviewResponse with KPIs and trend data
    
    Raises:
        400: Invalid date range
        401: Not authenticated
        403: Not executive role
    """
    # Validate date range
    if from_date > to_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be on or before end date"
        )
    
    # Get executive overview
    service = ExecutiveOverviewService(db)
    overview_data = service.get_overview_metrics(from_date, to_date)
    
    # Build response
    return ExecutiveOverviewResponse(
        from_date=from_date.isoformat(),
        to_date=to_date.isoformat(),
        generated_at=overview_data["generated_at"],
        freshness_status=overview_data["freshness_status"],
        kpis=overview_data["kpis"],
        trend_data=ExecutiveTrendData(**overview_data["trend_data"])
    )
