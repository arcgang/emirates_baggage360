"""Passenger case view model."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class PassengerCaseView(Base):
    """Passenger-safe case status projection."""
    
    __tablename__ = "passenger_case_views"
    __table_args__ = (
        UniqueConstraint("case_id", name="uq_case_view"),
        UniqueConstraint("case_reference", name="uq_case_reference_view"),
    )
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("exception_cases.id"), nullable=False, index=True)
    case_reference: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    latest_confirmed_status: Mapped[str] = mapped_column(String(255), nullable=False)
    estimated_notice: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_expected_update: Mapped[str] = mapped_column(String(255), nullable=False)
    passenger_safe_payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    refreshed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
