"""Executive metrics repository."""
import uuid
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.executive_metrics import ExecutiveDailyMetric


class ExecutiveMetricsRepository:
    """Repository for executive daily metrics persistence and retrieval."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_metrics_by_date_range(
        self,
        from_date: date,
        to_date: date,
        station_code: str | None = None
    ) -> list[ExecutiveDailyMetric]:
        """
        Retrieve executive metrics for a date range.
        
        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)
            station_code: Optional station filter (e.g., 'DXB')
        
        Returns:
            List of ExecutiveDailyMetric instances
        """
        query = self.db.query(ExecutiveDailyMetric).filter(
            and_(
                ExecutiveDailyMetric.metric_date >= from_date,
                ExecutiveDailyMetric.metric_date <= to_date
            )
        )
        
        if station_code:
            query = query.filter(ExecutiveDailyMetric.station_code == station_code)
        
        return query.order_by(ExecutiveDailyMetric.metric_date.asc()).all()
    
    def aggregate_daily(
        self,
        metric_date: date,
        station_code: str,
        open_case_count: int,
        urgent_case_count: int,
        recovered_before_departure_count: int,
        impacted_passenger_count: int,
        stale_data_case_count: int,
    ) -> ExecutiveDailyMetric:
        """
        Create or update executive daily metrics for a specific date and station.
        Enforces unique constraint on (metric_date, station_code).
        
        Args:
            metric_date: Date for the metric snapshot
            station_code: Station code (e.g., 'DXB')
            open_case_count: Number of open cases
            urgent_case_count: Number of urgent cases (critical + high severity)
            recovered_before_departure_count: Number of bags recovered before departure
            impacted_passenger_count: Number of passengers impacted
            stale_data_case_count: Number of cases with stale data sources
        
        Returns:
            Created or updated ExecutiveDailyMetric instance
        """
        # Check for existing metric
        existing = self.db.query(ExecutiveDailyMetric).filter(
            and_(
                ExecutiveDailyMetric.metric_date == metric_date,
                ExecutiveDailyMetric.station_code == station_code
            )
        ).first()
        
        if existing:
            # Update existing metric
            existing.open_case_count = open_case_count
            existing.urgent_case_count = urgent_case_count
            existing.recovered_before_departure_count = recovered_before_departure_count
            existing.impacted_passenger_count = impacted_passenger_count
            existing.stale_data_case_count = stale_data_case_count
            existing.snapshot_generated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new metric
            metric = ExecutiveDailyMetric(
                id=str(uuid.uuid4()),
                metric_date=metric_date,
                station_code=station_code,
                open_case_count=open_case_count,
                urgent_case_count=urgent_case_count,
                recovered_before_departure_count=recovered_before_departure_count,
                impacted_passenger_count=impacted_passenger_count,
                stale_data_case_count=stale_data_case_count,
                snapshot_generated_at=datetime.now(timezone.utc),
            )
            self.db.add(metric)
            self.db.commit()
            self.db.refresh(metric)
            return metric
