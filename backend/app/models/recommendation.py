"""Recommendation model."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .approval import ApprovalDecision
    from .exception_case import ExceptionCase
    from .task import Task


class Recommendation(Base):
    """Explainable recovery recommendation."""
    
    __tablename__ = "recommendations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("exception_cases.id"), nullable=False, index=True)
    action_code: Mapped[str] = mapped_column(String(50), nullable=False)
    action_label: Mapped[str] = mapped_column(String(255), nullable=False)
    reason_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    freshness_state: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    case: Mapped[ExceptionCase] = relationship("ExceptionCase", back_populates="recommendations")
    approvals: Mapped[list[ApprovalDecision]] = relationship("ApprovalDecision", back_populates="recommendation")
    tasks: Mapped[list[Task]] = relationship("Task", back_populates="recommendation")
