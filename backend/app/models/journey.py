"""Passenger journey and journey leg models."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .bag import Bag


class PassengerJourney(Base):
    """Passenger journey aggregate."""
    
    __tablename__ = "passenger_journeys"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    passenger_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    pnr_reference: Mapped[str] = mapped_column(String(50), nullable=False)
    itinerary_status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    legs: Mapped[list[JourneyLeg]] = relationship("JourneyLeg", back_populates="journey", cascade="all, delete-orphan")
    bags: Mapped[list[Bag]] = relationship("Bag", back_populates="journey")


class JourneyLeg(Base):
    """Flight leg within a passenger journey."""
    
    __tablename__ = "journey_legs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    journey_id: Mapped[str] = mapped_column(String(36), ForeignKey("passenger_journeys.id"), nullable=False, index=True)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    flight_number: Mapped[str] = mapped_column(String(20), nullable=False)
    departure_station: Mapped[str] = mapped_column(String(10), nullable=False)
    arrival_station: Mapped[str] = mapped_column(String(10), nullable=False)
    scheduled_departure_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    scheduled_arrival_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    actual_arrival_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    gate_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    stand_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    aircraft_registration: Mapped[str | None] = mapped_column(String(20), nullable=True)
    leg_status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    journey: Mapped[PassengerJourney] = relationship("PassengerJourney", back_populates="legs")
