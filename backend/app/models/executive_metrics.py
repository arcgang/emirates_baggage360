"""Executive daily metrics model."""
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class ExecutiveDailyMetric(Base):
    """Executive daily aggregated metrics."""
    
    __tablename__ = "executive_daily_metrics"
    __table_args__ = (
        UniqueConstraint("metric_date", "station_code", name="uq_daily_station_metric"),
    )
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    station_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    open_case_count: Mapped[int] = mapped_column(Integer, nullable=False)
    urgent_case_count: Mapped[int] = mapped_column(Integer, nullable=False)
    recovered_before_departure_count: Mapped[int] = mapped_column(Integer, nullable=False)
    impacted_passenger_count: Mapped[int] = mapped_column(Integer, nullable=False)
    stale_data_case_count: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
