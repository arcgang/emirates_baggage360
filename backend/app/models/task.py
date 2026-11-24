"""Task and task evidence models."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .exception_case import ExceptionCase
    from .recommendation import Recommendation


class Task(Base):
    """Operational task dispatched to partner or internal roles."""
    
    __tablename__ = "tasks"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("exception_cases.id"), nullable=False, index=True)
    recommendation_id: Mapped[str] = mapped_column(String(36), ForeignKey("recommendations.id"), nullable=False, index=True)
    assigned_role_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    assigned_partner_org_code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    bag_reference: Mapped[str] = mapped_column(String(50), nullable=False)
    station_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    flight_context_text: Mapped[str] = mapped_column(Text, nullable=False)
    instruction_text: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_links_json: Mapped[str] = mapped_column(Text, nullable=False)
    deadline_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    status_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    case: Mapped[ExceptionCase] = relationship("ExceptionCase", back_populates="tasks")
    recommendation: Mapped[Recommendation] = relationship("Recommendation", back_populates="tasks")
    evidence: Mapped[list[TaskEvidence]] = relationship("TaskEvidence", back_populates="task", cascade="all, delete-orphan")


class TaskEvidence(Base):
    """Evidence submitted for task completion."""
    
    __tablename__ = "task_evidence"
    __table_args__ = (
        UniqueConstraint("client_event_id", name="uq_client_event_id"),
    )
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    actor_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    note_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    evidence_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client_event_id: Mapped[str] = mapped_column(String(255), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    task: Mapped[Task] = relationship("Task", back_populates="evidence")
