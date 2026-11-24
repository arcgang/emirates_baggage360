"""Bag and bag event models."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .journey import PassengerJourney


class Bag(Base):
    """Bag aggregate with current state."""
    
    __tablename__ = "bags"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bag_tag: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    journey_id: Mapped[str] = mapped_column(String(36), ForeignKey("passenger_journeys.id"), nullable=False, index=True)
    latest_confirmed_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    current_case_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    current_status_code: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    journey: Mapped[PassengerJourney] = relationship("PassengerJourney", back_populates="bags")
    events: Mapped[list[BagEvent]] = relationship("BagEvent", back_populates="bag", cascade="all, delete-orphan")


class BagEvent(Base):
    """Immutable bag event from source systems."""
    
    __tablename__ = "bag_events"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    bag_id: Mapped[str] = mapped_column(String(36), ForeignKey("bags.id"), nullable=False, index=True)
    source_event_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    source_system: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_station: Mapped[str | None] = mapped_column(String(10), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    fact_type: Mapped[str] = mapped_column(String(50), nullable=False)
    freshness_state: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    
    bag: Mapped[Bag] = relationship("Bag", back_populates="events")
