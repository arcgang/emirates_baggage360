"""Bag journey service for composing bag timelines and journey context."""
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..repositories.bag_repository import BagEventRepository, BagRepository
from ..repositories.journey_repository import JourneyRepository
from ..schemas.operations_schemas import BagMilestone, BagTimeline, JourneyContext


class BagJourneyService:
    """Service for baggage journey visibility and context correlation."""
    
    def __init__(self, db: Session):
        self.db = db
        self.bag_repo = BagRepository(db)
        self.bag_event_repo = BagEventRepository(db)
        self.journey_repo = JourneyRepository(db)
    
    def compose_bag_timeline(self, bag_id: str) -> BagTimeline | None:
        """
        Compose a complete bag timeline with milestones and journey context.
        
        Returns:
            BagTimeline with milestones marked observed/derived/estimated,
            source system labels, freshness state, and journey context.
        """
        bag = self.bag_repo.get_by_id(bag_id)
        if not bag:
            return None
        
        # Get all events for this bag
        events = self.bag_event_repo.get_by_bag(bag_id)
        
        # Convert events to milestones
        milestones = []
        now = datetime.now(timezone.utc)
        freshness_threshold = timedelta(minutes=30)
        
        for event in events:
            # Calculate freshness state
            age = now - event.observed_at
            if age > freshness_threshold:
                freshness_state = "stale"
            else:
                freshness_state = "fresh"
            
            milestone = BagMilestone(
                event_type=event.event_type,
                observed_at=event.observed_at,
                source_system=event.source_system,
                fact_type=event.fact_type,
                freshness_state=freshness_state,
                location_code=event.event_station
            )
            milestones.append(milestone)
        
        # Get journey context
        journey_context = self._compose_journey_context(bag.journey_id)
        
        # Mask passenger name for operations view
        passenger_name_masked = self._mask_passenger_name(bag.journey.passenger_reference)
        
        return BagTimeline(
            bag_id=bag.id,
            bag_tag=bag.bag_tag,
            passenger_name_masked=passenger_name_masked,
            journey_context=journey_context,
            milestones=milestones
        )
    
    def _compose_journey_context(self, journey_id: str) -> JourneyContext | None:
        """
        Compose journey context showing inbound/onward flights,
        connection window, and operational changes.
        """
        journey = self.journey_repo.get_by_id(journey_id)
        if not journey:
            return None
        
        legs = self.journey_repo.get_legs_by_journey(journey_id)
        if not legs:
            return None
        
        # Find inbound (arrived) and onward (scheduled) legs
        inbound_leg = None
        onward_leg = None
        
        for leg in legs:
            if leg.leg_status == "arrived" and not inbound_leg:
                inbound_leg = leg
            elif leg.leg_status == "scheduled" and not onward_leg:
                onward_leg = leg
        
        if not inbound_leg or not onward_leg:
            # If we don't have both legs, use first two legs
            if len(legs) >= 2:
                inbound_leg = legs[0]
                onward_leg = legs[1]
            else:
                return None
        
        # Calculate connection window
        connection_window_minutes = 0
        if inbound_leg.actual_arrival_at and onward_leg.scheduled_departure_at:
            connection_window = onward_leg.scheduled_departure_at - inbound_leg.actual_arrival_at
            connection_window_minutes = int(connection_window.total_seconds() / 60)
        elif inbound_leg.scheduled_arrival_at and onward_leg.scheduled_departure_at:
            connection_window = onward_leg.scheduled_departure_at - inbound_leg.scheduled_arrival_at
            connection_window_minutes = int(connection_window.total_seconds() / 60)
        
        # Detect changes (gate, stand, aircraft)
        gate_change = None
        stand_change = None
        aircraft_change = None
        
        # For demo purposes, we'll detect changes by checking if codes exist
        # In a real system, this would compare against baseline itinerary
        if onward_leg.gate_code and onward_leg.gate_code != inbound_leg.gate_code:
            gate_change = f"Changed to {onward_leg.gate_code}"
        
        if onward_leg.stand_code and onward_leg.stand_code != inbound_leg.stand_code:
            stand_change = f"Changed to {onward_leg.stand_code}"
        
        if onward_leg.aircraft_registration and onward_leg.aircraft_registration != inbound_leg.aircraft_registration:
            aircraft_change = f"Changed to {onward_leg.aircraft_registration}"
        
        return JourneyContext(
            journey_id=journey.id,
            inbound_flight=f"{inbound_leg.flight_number} {inbound_leg.departure_station}-{inbound_leg.arrival_station}",
            onward_flight=f"{onward_leg.flight_number} {onward_leg.departure_station}-{onward_leg.arrival_station}",
            connection_window_minutes=connection_window_minutes,
            gate_change=gate_change,
            stand_change=stand_change,
            aircraft_change=aircraft_change
        )
    
    def _mask_passenger_name(self, passenger_reference: str) -> str:
        """Mask passenger name for privacy."""
        # In demo, passenger_reference is like "PAX-20241101-001"
        # We'll return a masked version like "PAX-***-001"
        parts = passenger_reference.split("-")
        if len(parts) >= 3:
            return f"{parts[0]}-***-{parts[-1]}"
        return "***"
