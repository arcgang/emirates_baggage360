"""Executive overview service for aggregated reliability and impact metrics."""
from datetime import date, datetime, timezone

from sqlalchemy import and_
from sqlalchemy.orm import Session

from ..models.approval import ApprovalDecision
from ..models.exception_case import ExceptionCase
from ..repositories.executive_metrics_repository import ExecutiveMetricsRepository


class ExecutiveOverviewService:
    """
    Service for executive reliability and impact overview.
    Implements FR-017: Executive reliability and impact overview with aggregated insight.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ExecutiveMetricsRepository(db)
    
    def get_overview_metrics(
        self,
        from_date: date,
        to_date: date,
        station_code: str | None = None
    ) -> dict:
        """
        Get executive overview metrics aggregating exception cases, approval decisions,
        tasks, and bag events over a date range.
        
        Returns KPIs:
        - Exception rate per 1000 bags
        - Recovered within cutoff percentage
        - Mean time to decision (minutes)
        - Passengers impacted
        - Open case ageing (hours)
        - Data freshness counts (fresh vs stale sources)
        
        Args:
            from_date: Start date (inclusive)
            to_date: End date (inclusive)
            station_code: Optional station code filter (aggregates all stations if None)
        
        Returns:
            Dictionary with KPIs, trend data, generated timestamp, and freshness status
        """
        # Retrieve persisted daily metrics (aggregates across all stations if station_code is None)
        daily_metrics = self.repo.get_metrics_by_date_range(from_date, to_date, station_code)
        
        if not daily_metrics:
            # No persisted metrics, return empty state
            return {
                "kpis": [],
                "trend_data": {
                    "dates": [],
                    "exception_rate_per_1000": [],
                    "recovered_within_cutoff_pct": [],
                    "passengers_impacted": [],
                    "open_case_count": [],
                    "stale_data_case_count": []
                },
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "freshness_status": "no_data"
            }
        
        # Aggregate KPIs from daily metrics
        total_open_cases = sum(m.open_case_count for m in daily_metrics)
        total_recovered = sum(m.recovered_before_departure_count for m in daily_metrics)
        total_passengers_impacted = sum(m.impacted_passenger_count for m in daily_metrics)
        total_stale_data_cases = sum(m.stale_data_case_count for m in daily_metrics)
        
        # Calculate derived KPIs
        # Exception rate: assuming 1000 bags processed per day on average
        days_count = len(daily_metrics)
        total_bags_processed = days_count * 1000  # Simplified assumption
        exception_rate = (total_open_cases / total_bags_processed) * 1000 if total_bags_processed > 0 else 0.0
        
        # Recovered within cutoff percentage
        recovered_pct = (total_recovered / total_open_cases) * 100 if total_open_cases > 0 else 0.0
        
        # Mean time to decision: aggregate approval decisions in date range
        mean_decision_time = self._calculate_mean_decision_time(from_date, to_date)
        
        # Open case ageing: average hours open for currently open cases
        open_case_ageing = self._calculate_open_case_ageing()
        
        # Data freshness status
        freshness_status = "mixed" if total_stale_data_cases > 0 else "fresh"
        
        # Build KPI list
        kpis = [
            {
                "metric_code": "exception_rate",
                "metric_label": "Exception Rate (per 1000 bags)",
                "current_value": round(exception_rate, 2),
                "trend_direction": "flat",  # Simplified for demo
                "passenger_impact_note": f"{total_passengers_impacted} passengers impacted"
            },
            {
                "metric_code": "recovered_within_cutoff",
                "metric_label": "Recovered Within Cutoff (%)",
                "current_value": round(recovered_pct, 1),
                "trend_direction": "flat",
                "passenger_impact_note": f"{total_recovered} bags recovered before departure"
            },
            {
                "metric_code": "mean_time_to_decision",
                "metric_label": "Mean Time to Decision (minutes)",
                "current_value": round(mean_decision_time, 1),
                "trend_direction": "flat",
                "passenger_impact_note": None
            },
            {
                "metric_code": "passengers_impacted",
                "metric_label": "Passengers Impacted",
                "current_value": total_passengers_impacted,
                "trend_direction": "flat",
                "passenger_impact_note": "Connecting passengers with a bag at risk."
            },
            {
                "metric_code": "open_cases",
                "metric_label": "Open Cases",
                "current_value": total_open_cases,
                "trend_direction": "flat",
                "passenger_impact_note": f"{total_open_cases} cases currently open"
            },
            {
                "metric_code": "open_case_ageing",
                "metric_label": "Open Case Ageing (hours)",
                "current_value": round(open_case_ageing, 1),
                "trend_direction": "flat",
                "passenger_impact_note": f"{total_open_cases} open cases"
            },
            {
                "metric_code": "stale_data_cases",
                "metric_label": "Cases with Stale Data",
                "current_value": total_stale_data_cases,
                "trend_direction": "flat",
                "passenger_impact_note": f"{total_stale_data_cases} of {total_open_cases} sources"
            }
        ]
        
        # Build trend data (daily values)
        trend_data = {
            "dates": [m.metric_date.isoformat() for m in daily_metrics],
            "exception_rate_per_1000": [
                round((m.open_case_count / 1000.0) * 1000, 2) for m in daily_metrics
            ],
            "recovered_within_cutoff_pct": [
                round((m.recovered_before_departure_count / m.open_case_count) * 100, 1) if m.open_case_count > 0 else 0.0
                for m in daily_metrics
            ],
            "passengers_impacted": [m.impacted_passenger_count for m in daily_metrics],
            "open_case_count": [m.open_case_count for m in daily_metrics],
            "stale_data_case_count": [m.stale_data_case_count for m in daily_metrics],
        }
        
        return {
            "kpis": kpis,
            "trend_data": trend_data,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "freshness_status": freshness_status
        }
    
    def _calculate_mean_decision_time(self, from_date: date, to_date: date) -> float:
        """
        Calculate mean time from case creation to approval decision.
        
        Args:
            from_date: Start date
            to_date: End date
        
        Returns:
            Mean decision time in minutes
        """
        # Query approval decisions within date range
        decisions = (
            self.db.query(ApprovalDecision)
            .filter(
                and_(
                    ApprovalDecision.decided_at >= datetime.combine(from_date, datetime.min.time()),
                    ApprovalDecision.decided_at <= datetime.combine(to_date, datetime.max.time())
                )
            )
            .all()
        )
        
        if not decisions:
            return 0.0
        
        # Calculate time from case creation to decision
        decision_times = []
        for decision in decisions:
            case = self.db.query(ExceptionCase).filter(ExceptionCase.id == decision.case_id).first()
            if case:
                time_diff = decision.decided_at - case.created_at
                decision_times.append(time_diff.total_seconds() / 60.0)  # Convert to minutes
        
        return sum(decision_times) / len(decision_times) if decision_times else 0.0
    
    def _calculate_open_case_ageing(self) -> float:
        """
        Calculate average ageing (hours) for currently open cases.
        
        Returns:
            Mean case age in hours
        """
        now = datetime.now(timezone.utc)
        
        open_cases = (
            self.db.query(ExceptionCase)
            .filter(ExceptionCase.status_code == "open")
            .all()
        )
        
        if not open_cases:
            return 0.0
        
        # Ensure created_at is timezone-aware for comparison
        ages = [
            (now - (case.created_at.replace(tzinfo=timezone.utc) if case.created_at.tzinfo is None else case.created_at)).total_seconds() / 3600.0
            for case in open_cases
        ]
        return sum(ages) / len(ages)
