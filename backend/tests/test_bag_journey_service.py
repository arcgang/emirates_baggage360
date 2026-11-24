"""Tests for bag journey service."""
import uuid
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from sqlalchemy.orm import Session
from app.models.bag import Bag, BagEvent
from app.models.journey import PassengerJourney, JourneyLeg
from app.services.bag_journey_service import BagJourneyService


@pytest.fixture
def test_journey(db_session: Session) -> PassengerJourney:
    """Create a test journey."""
    journey = PassengerJourney(
        id=str(uuid.UUID(int=9001)),
        passenger_reference="PAX-TEST-001",
        pnr_reference="TESTPNR",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(journey)
    db_session.commit()
    return journey


@pytest.fixture
def test_journey_legs(db_session: Session, test_journey: PassengerJourney) -> list[JourneyLeg]:
    """Create test journey legs."""
    now = datetime.now(timezone.utc)
    
    inbound_leg = JourneyLeg(
        id=str(uuid.UUID(int=9101)),
        journey_id=test_journey.id,
        sequence_number=1,
        flight_number="EK001",
        departure_station="LHR",
        arrival_station="DXB",
        scheduled_departure_at=now - timedelta(hours=6),
        scheduled_arrival_at=now - timedelta(hours=1),
        actual_arrival_at=now - timedelta(hours=1, minutes=15),
        gate_code="A12",
        stand_code="12",
        aircraft_registration="A6-EUA",
        leg_status="arrived",
        created_at=now,
        updated_at=now,
    )
    
    onward_leg = JourneyLeg(
        id=str(uuid.UUID(int=9102)),
        journey_id=test_journey.id,
        sequence_number=2,
        flight_number="EK101",
        departure_station="DXB",
        arrival_station="SYD",
        scheduled_departure_at=now + timedelta(hours=2),
        scheduled_arrival_at=now + timedelta(hours=14),
        gate_code="B05",
        stand_code="45",
        aircraft_registration="A6-EUB",
        leg_status="scheduled",
        created_at=now,
        updated_at=now,
    )
    
    db_session.add(inbound_leg)
    db_session.add(onward_leg)
    db_session.commit()
    return [inbound_leg, onward_leg]


@pytest.fixture
def test_bag_at_risk(db_session: Session, test_journey: PassengerJourney) -> Bag:
    """Create a test bag with at-risk status."""
    bag = Bag(
        id=str(uuid.UUID(int=9201)),
        bag_tag="TEST001",
        journey_id=test_journey.id,
        current_status_code="at_risk",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(bag)
    db_session.commit()
    return bag


@pytest.fixture
def test_bag_on_time(db_session: Session, test_journey: PassengerJourney) -> Bag:
    """Create a test bag with on-time status."""
    bag = Bag(
        id=str(uuid.UUID(int=9202)),
        bag_tag="TEST002",
        journey_id=test_journey.id,
        current_status_code="on_time",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(bag)
    db_session.commit()
    return bag


@pytest.fixture
def test_events_at_risk(db_session: Session, test_bag_at_risk: Bag) -> list[BagEvent]:
    """Create test events for at-risk bag."""
    now = datetime.now(timezone.utc)
    
    events = [
        BagEvent(
            id=str(uuid.UUID(int=9301)),
            bag_id=test_bag_at_risk.id,
            source_event_key="TEST-001-001",
            source_system="Wasla",
            event_type="acceptance",
            event_station="LHR",
            observed_at=now - timedelta(hours=6),
            ingested_at=now - timedelta(hours=6),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "accepted"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=9302)),
            bag_id=test_bag_at_risk.id,
            source_event_key="TEST-001-002",
            source_system="BHS",
            event_type="loaded",
            event_station="LHR",
            observed_at=now - timedelta(hours=5),
            ingested_at=now - timedelta(hours=5),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "loaded", "flight": "EK001"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=9303)),
            bag_id=test_bag_at_risk.id,
            source_event_key="TEST-001-003",
            source_system="BRS",
            event_type="arrived",
            event_station="DXB",
            observed_at=now - timedelta(hours=1, minutes=15),
            ingested_at=now - timedelta(hours=1, minutes=15),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "arrived", "location": "DXB"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=9304)),
            bag_id=test_bag_at_risk.id,
            source_event_key="TEST-001-004",
            source_system="flight_ops",
            event_type="transfer_pending",
            event_station="DXB",
            observed_at=now - timedelta(minutes=45),
            ingested_at=now - timedelta(minutes=45),
            fact_type="derived",
            freshness_state="stale",
            confidence_score=Decimal("0.75"),
            payload_json=json.dumps({"event": "transfer_pending"}),
        ),
    ]
    
    for event in events:
        db_session.add(event)
    db_session.commit()
    return events


@pytest.fixture
def test_events_on_time(db_session: Session, test_bag_on_time: Bag) -> list[BagEvent]:
    """Create test events for on-time bag."""
    now = datetime.now(timezone.utc)
    
    events = [
        BagEvent(
            id=str(uuid.UUID(int=9401)),
            bag_id=test_bag_on_time.id,
            source_event_key="TEST-002-001",
            source_system="Wasla",
            event_type="acceptance",
            event_station="LHR",
            observed_at=now - timedelta(hours=6),
            ingested_at=now - timedelta(hours=6),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "accepted"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=9402)),
            bag_id=test_bag_on_time.id,
            source_event_key="TEST-002-002",
            source_system="Wasla",
            event_type="transfer_confirmed",
            event_station="DXB",
            observed_at=now - timedelta(minutes=10),
            ingested_at=now - timedelta(minutes=10),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "transfer_confirmed", "target_flight": "EK101"}),
        ),
    ]
    
    for event in events:
        db_session.add(event)
    db_session.commit()
    return events


def test_compose_bag_timeline_at_risk(
    db_session: Session,
    test_journey: PassengerJourney,
    test_journey_legs: list[JourneyLeg],
    test_bag_at_risk: Bag,
    test_events_at_risk: list[BagEvent]
):
    """Test timeline composition for at-risk bag."""
    service = BagJourneyService(db_session)
    timeline = service.compose_bag_timeline(test_bag_at_risk.id)
    
    assert timeline is not None
    assert timeline.bag_id == test_bag_at_risk.id
    assert timeline.bag_tag == "TEST001"
    assert timeline.passenger_name_masked == "PAX-***-001"
    
    # Check milestones
    assert len(timeline.milestones) == 4
    
    # Check milestone types
    milestone_types = [m.event_type for m in timeline.milestones]
    assert "acceptance" in milestone_types
    assert "loaded" in milestone_types
    assert "arrived" in milestone_types
    assert "transfer_pending" in milestone_types
    
    # Check fact types
    observed_count = sum(1 for m in timeline.milestones if m.fact_type == "observed")
    derived_count = sum(1 for m in timeline.milestones if m.fact_type == "derived")
    assert observed_count == 3
    assert derived_count == 1
    
    # Check source systems
    source_systems = [m.source_system for m in timeline.milestones]
    assert "Wasla" in source_systems
    assert "BHS" in source_systems
    assert "BRS" in source_systems
    assert "flight_ops" in source_systems
    
    # Check freshness labeling (at least one stale)
    stale_count = sum(1 for m in timeline.milestones if m.freshness_state == "stale")
    assert stale_count >= 1


def test_compose_bag_timeline_on_time(
    db_session: Session,
    test_journey: PassengerJourney,
    test_journey_legs: list[JourneyLeg],
    test_bag_on_time: Bag,
    test_events_on_time: list[BagEvent]
):
    """Test timeline composition for on-time bag."""
    service = BagJourneyService(db_session)
    timeline = service.compose_bag_timeline(test_bag_on_time.id)
    
    assert timeline is not None
    assert timeline.bag_id == test_bag_on_time.id
    assert timeline.bag_tag == "TEST002"
    
    # Check milestones
    assert len(timeline.milestones) == 2
    
    # Check all events are observed (confirmed)
    for milestone in timeline.milestones:
        assert milestone.fact_type == "observed"


def test_journey_context_correlation(
    db_session: Session,
    test_journey: PassengerJourney,
    test_journey_legs: list[JourneyLeg],
    test_bag_at_risk: Bag,
    test_events_at_risk: list[BagEvent]
):
    """Test journey context includes inbound/onward flights and connection window."""
    service = BagJourneyService(db_session)
    timeline = service.compose_bag_timeline(test_bag_at_risk.id)
    
    assert timeline is not None
    assert timeline.journey_context is not None
    
    journey_ctx = timeline.journey_context
    assert journey_ctx.journey_id == test_journey.id
    assert "EK001" in journey_ctx.inbound_flight
    assert "LHR-DXB" in journey_ctx.inbound_flight
    assert "EK101" in journey_ctx.onward_flight
    assert "DXB-SYD" in journey_ctx.onward_flight
    
    # Connection window should be calculated
    assert journey_ctx.connection_window_minutes > 0


def test_freshness_calculation(
    db_session: Session,
    test_journey: PassengerJourney,
    test_journey_legs: list[JourneyLeg],
    test_bag_at_risk: Bag,
    test_events_at_risk: list[BagEvent]
):
    """Test freshness state calculation based on observed_at timestamp."""
    service = BagJourneyService(db_session)
    timeline = service.compose_bag_timeline(test_bag_at_risk.id)
    
    assert timeline is not None
    
    # Recent events should be fresh, old events should be stale
    for milestone in timeline.milestones:
        assert milestone.freshness_state in ["fresh", "stale", "awaiting_confirmation"]


def test_bag_not_found(db_session: Session):
    """Test that None is returned for non-existent bag."""
    service = BagJourneyService(db_session)
    timeline = service.compose_bag_timeline(str(uuid.UUID(int=99999)))
    
    assert timeline is None


def test_passenger_name_masking(
    db_session: Session,
    test_journey: PassengerJourney,
    test_journey_legs: list[JourneyLeg],
    test_bag_at_risk: Bag,
    test_events_at_risk: list[BagEvent]
):
    """Test that passenger names are masked for privacy."""
    service = BagJourneyService(db_session)
    timeline = service.compose_bag_timeline(test_bag_at_risk.id)
    
    assert timeline is not None
    assert "***" in timeline.passenger_name_masked
    assert "PAX-TEST-001" not in timeline.passenger_name_masked
