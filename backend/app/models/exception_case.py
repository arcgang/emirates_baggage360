"""Exception case and case-bag membership models."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .approval import ApprovalDecision
    from .recommendation import Recommendation
    from .task import Task


class ExceptionCase(Base):
    """Exception case aggregate."""
    
    __tablename__ = "exception_cases"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_reference: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    exception_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity_code: Mapped[str] = mapped_column(String(50), nullable=False)
    deadline_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    status_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    observed_state_summary: Mapped[str] = mapped_column(Text, nullable=False)
    predicted_state_summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    case_bags: Mapped[list[CaseBag]] = relationship("CaseBag", back_populates="case", cascade="all, delete-orphan")
    recommendations: Mapped[list[Recommendation]] = relationship("Recommendation", back_populates="case")
    approvals: Mapped[list[ApprovalDecision]] = relationship("ApprovalDecision", back_populates="case")
    tasks: Mapped[list[Task]] = relationship("Task", back_populates="case")


class CaseBag(Base):
    """Many-to-many link between cases and bags."""
    
    __tablename__ = "case_bags"
    
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("exception_cases.id"), primary_key=True, index=True)
    bag_id: Mapped[str] = mapped_column(String(36), ForeignKey("bags.id"), primary_key=True, index=True)
    primary_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    case: Mapped[ExceptionCase] = relationship("ExceptionCase", back_populates="case_bags")
