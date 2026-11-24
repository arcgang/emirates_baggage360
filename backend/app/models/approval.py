"""Approval decision model."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .exception_case import ExceptionCase
    from .recommendation import Recommendation


class ApprovalDecision(Base):
    """Human approval decision for recommendations."""
    
    __tablename__ = "approval_decisions"
    __table_args__ = (
        UniqueConstraint("case_id", "recommendation_id", "decision_version", name="uq_approval_version"),
    )
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("exception_cases.id"), nullable=False, index=True)
    recommendation_id: Mapped[str] = mapped_column(String(36), ForeignKey("recommendations.id"), nullable=False, index=True)
    decided_by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    decision_code: Mapped[str] = mapped_column(String(50), nullable=False)
    rationale_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    decision_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    case: Mapped[ExceptionCase] = relationship("ExceptionCase", back_populates="approvals")
    recommendation: Mapped[Recommendation] = relationship("Recommendation", back_populates="approvals")
