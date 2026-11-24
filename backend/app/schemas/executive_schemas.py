"""Executive-facing Pydantic schemas for reliability and impact overview."""
from pydantic import BaseModel, ConfigDict


class ExecutiveKPI(BaseModel):
    """
    Individual executive KPI (Key Performance Indicator).
    Includes metric code, label, current value, trend direction, and passenger impact note.
    """
    metric_code: str  # exception_rate, recovered_within_cutoff, mean_time_to_decision, etc.
    metric_label: str  # Human-readable label
    current_value: float  # Current metric value
    trend_direction: str  # up, down, flat
    passenger_impact_note: str | None = None  # Contextual note about passenger impact
    
    model_config = ConfigDict(from_attributes=True)


class ExecutiveTrendData(BaseModel):
    """
    Trend data showing daily metric values over the requested date range.
    Supports time-based review of trends.
    """
    dates: list[str]  # ISO date strings
    exception_rate_per_1000: list[float]
    recovered_within_cutoff_pct: list[float]
    passengers_impacted: list[int]
    open_case_count: list[int]
    stale_data_case_count: list[int]
    
    model_config = ConfigDict(from_attributes=True)


class ExecutiveOverviewResponse(BaseModel):
    """
    Executive overview response schema.
    Returns aggregated KPIs and trend data for a date range.
    Implements FR-017: high-level summary of exception, recovery, and passenger impact indicators.
    """
    from_date: str  # ISO date
    to_date: str  # ISO date
    generated_at: str  # ISO datetime
    freshness_status: str  # fresh, stale, mixed, no_data
    kpis: list[ExecutiveKPI]
    trend_data: ExecutiveTrendData
    
    model_config = ConfigDict(from_attributes=True)
