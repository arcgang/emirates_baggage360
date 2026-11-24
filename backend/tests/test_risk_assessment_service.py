"""Tests for risk assessment service."""
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import pytest
from sqlalchemy.orm import Session

from app.models.bag import Bag, BagEvent
from app.models.exception_case import ExceptionCase
from app.models.journey import PassengerJourney, JourneyLeg
from app.services.risk_assessment_service import RiskAssessmentService


def test_calculate_connection_risk_critical(db_session: Session):
    """Test connection risk calculation for critical risk scenario."""
    # Create journey
    journey = PassengerJourney(
        id=str(uuid.UUID(int=1)),
        passenger_reference="PAX-001",
        pnr_reference="PNR001",
        itinerary_status="active"
    )
    db_session.add(journey)
    
    # Create legs with tight connection
    now = datetime.now(timezone.utc)
    inbound = JourneyLeg(
        id=str(uuid.UUID(int=2)),
        journey_id=journey.id,
        sequence_number=1,
        flight_number="EK001",
        departure_station="LHR",
        arrival_station="DXB",
        scheduled_departure_at=now - timedelta(hours=6),
        scheduled_arrival_at=now - timedelta(hours=1),
        actual_arrival_at=now - timedelta(hours=1, minutes=15),
        leg_status="arrived"
    )
    onward = JourneyLeg(
        id=str(uuid.UUID(int=3)),
        journey_id=journey.id,
        sequence_number=2,
        flight_number="EK101",
        departure_station="DXB",
        arrival_station="SYD",
        scheduled_departure_at=now + timedelta(minutes=120),  # 2 hours from now, cutoff in 30 min
        scheduled_arrival_at=now + timedelta(hours=14),
        leg_status="scheduled"
    )
    db_session.add_all([inbound, onward])
    
    # Create bag
    bag = Bag(
        id=str(uuid.UUID(int=4)),
        bag_tag="EK123",
        journey_id=journey.id,
        current_status_code="in_transfer"
    )
    db_session.add(bag)
    
    # Create latest event (transfer pending, derived)
    event = BagEvent(
        id=str(uuid.UUID(int=5)),
        bag_id=bag.id,
        source_event_key="TEST-001",
        source_system="flight_ops",
        event_type="transfer_pending",
        event_station="DXB",
        observed_at=now - timedelta(minutes=5),
        ingested_at=now - timedelta(minutes=5),
        fact_type="derived",
        freshness_state="fresh",
        confidence_score=Decimal("0.75"),
        payload_json=json.dumps({})
    )
    db_session.add(event)
    
    # Create case
    case = ExceptionCase(
        id=str(uuid.UUID(int=6)),
        case_reference="CASE-001",
        exception_type="short_connection_risk",
        severity_code="critical",
        deadline_at=now + timedelta(minutes=120),
        status_code="open",
        observed_state_summary="Test",
        predicted_state_summary="Test",
        created_by_user_id=str(uuid.UUID(int=1))
    )
    db_session.add(case)
    db_session.commit()
    
    # Test
    service = RiskAssessmentService(db_session)
    result = service.calculate_connection_risk(bag, case, event)
    
    assert result["risk_label"] == "Critical: transfer scan missing, approaching cutoff"
    assert result["urgency_rank"] == 1
    assert 28 <= result["time_to_cutoff_minutes"] <= 31  # Allow for execution time
    assert "transfer_pending" in result["observed_state_summary"]
    assert "Critical" in result["predicted_state_summary"]


def test_calculate_connection_risk_late_inbound(db_session: Session):
    """Test connection risk calculation for late inbound scenario."""
    # Create journey
    journey = PassengerJourney(
        id=str(uuid.UUID(int=1)),
        passenger_reference="PAX-001",
        pnr_reference="PNR001",
        itinerary_status="active"
    )
    db_session.add(journey)
    
    # Create legs with medium connection window
    now = datetime.now(timezone.utc)
    inbound = JourneyLeg(
        id=str(uuid.UUID(int=2)),
        journey_id=journey.id,
        sequence_number=1,
        flight_number="EK001",
        departure_station="LHR",
        arrival_station="DXB",
        scheduled_departure_at=now - timedelta(hours=6),
        scheduled_arrival_at=now - timedelta(hours=1),
        actual_arrival_at=now - timedelta(minutes=15),  # 45 min delay
        leg_status="arrived"
    )
    onward = JourneyLeg(
        id=str(uuid.UUID(int=3)),
        journey_id=journey.id,
        sequence_number=2,
        flight_number="EK101",
        departure_station="DXB",
        arrival_station="SYD",
        scheduled_departure_at=now + timedelta(hours=2),  # cutoff in 30 min
        scheduled_arrival_at=now + timedelta(hours=14),
        leg_status="scheduled"
    )
    db_session.add_all([inbound, onward])
    
    # Create bag
    bag = Bag(
        id=str(uuid.UUID(int=4)),
        bag_tag="EK123",
        journey_id=journey.id,
        current_status_code="in_transfer"
    )
    db_session.add(bag)
    
    # Create latest event (arrived)
    event = BagEvent(
        id=str(uuid.UUID(int=5)),
        bag_id=bag.id,
        source_event_key="TEST-001",
        source_system="BRS",
        event_type="arrived",
        event_station="DXB",
        observed_at=now - timedelta(minutes=15),
        ingested_at=now - timedelta(minutes=15),
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=Decimal("1.00"),
        payload_json=json.dumps({})
    )
    db_session.add(event)
    
    # Create case
    case = ExceptionCase(
        id=str(uuid.UUID(int=6)),
        case_reference="CASE-001",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=now + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test",
        predicted_state_summary="Test",
        created_by_user_id=str(uuid.UUID(int=1))
    )
    db_session.add(case)
    db_session.commit()
    
    # Test
    service = RiskAssessmentService(db_session)
    result = service.calculate_connection_risk(bag, case, event)
    
    assert "Connection at risk" in result["risk_label"] or "Critical" in result["risk_label"]
    assert result["urgency_rank"] <= 2
    assert 28 <= result["time_to_cutoff_minutes"] <= 31  # Allow for execution time
    assert "arrived" in result["observed_state_summary"]
    assert "delayed" in result["observed_state_summary"]


def test_calculate_connection_risk_moderate(db_session: Session):
    """Test connection risk calculation for moderate risk scenario."""
    # Create journey
    journey = PassengerJourney(
        id=str(uuid.UUID(int=1)),
        passenger_reference="PAX-001",
        pnr_reference="PNR001",
        itinerary_status="active"
    )
    db_session.add(journey)
    
    # Create legs with comfortable connection window
    now = datetime.now(timezone.utc)
    inbound = JourneyLeg(
        id=str(uuid.UUID(int=2)),
        journey_id=journey.id,
        sequence_number=1,
        flight_number="EK001",
        departure_station="LHR",
        arrival_station="DXB",
        scheduled_departure_at=now - timedelta(hours=6),
        scheduled_arrival_at=now - timedelta(hours=2),
        actual_arrival_at=now - timedelta(hours=2),
        leg_status="arrived"
    )
    onward = JourneyLeg(
        id=str(uuid.UUID(int=3)),
        journey_id=journey.id,
        sequence_number=2,
        flight_number="EK101",
        departure_station="DXB",
        arrival_station="SYD",
        scheduled_departure_at=now + timedelta(hours=3),  # cutoff in 90 min
        scheduled_arrival_at=now + timedelta(hours=14),
        leg_status="scheduled"
    )
    db_session.add_all([inbound, onward])
    
    # Create bag
    bag = Bag(
        id=str(uuid.UUID(int=4)),
        bag_tag="EK123",
        journey_id=journey.id,
        current_status_code="in_transfer"
    )
    db_session.add(bag)
    
    # Create latest event (transfer confirmed)
    event = BagEvent(
        id=str(uuid.UUID(int=5)),
        bag_id=bag.id,
        source_event_key="TEST-001",
        source_system="Wasla",
        event_type="transfer_confirmed",
        event_station="DXB",
        observed_at=now - timedelta(minutes=10),
        ingested_at=now - timedelta(minutes=10),
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=Decimal("1.00"),
        payload_json=json.dumps({})
    )
    db_session.add(event)
    
    # Create case
    case = ExceptionCase(
        id=str(uuid.UUID(int=6)),
        case_reference="CASE-001",
        exception_type="transfer_monitoring",
        severity_code="medium",
        deadline_at=now + timedelta(hours=3),
        status_code="open",
        observed_state_summary="Test",
        predicted_state_summary="Test",
        created_by_user_id=str(uuid.UUID(int=1))
    )
    db_session.add(case)
    db_session.commit()
    
    # Test
    service = RiskAssessmentService(db_session)
    result = service.calculate_connection_risk(bag, case, event)
    
    # With 90 min cutoff, the risk label could be "Connection at risk" or "Moderate"
    # depending on exact timing, so we check for reasonable urgency rank
    assert result["urgency_rank"] >= 2
    assert 88 <= result["time_to_cutoff_minutes"] <= 91  # Allow for execution time
    assert "transfer_confirmed" in result["observed_state_summary"]
    assert "EK101" in result["predicted_state_summary"]


def test_urgency_ranking(db_session: Session):
    """Test urgency ranking based on time to cutoff and severity."""
    # Create minimal journey
    journey = PassengerJourney(
        id=str(uuid.UUID(int=1)),
        passenger_reference="PAX-001",
        pnr_reference="PNR001",
        itinerary_status="active"
    )
    db_session.add(journey)
    
    now = datetime.now(timezone.utc)
    onward = JourneyLeg(
        id=str(uuid.UUID(int=2)),
        journey_id=journey.id,
        sequence_number=1,
        flight_number="EK101",
        departure_station="DXB",
        arrival_station="SYD",
        scheduled_departure_at=now + timedelta(minutes=60),
        scheduled_arrival_at=now + timedelta(hours=14),
        leg_status="scheduled"
    )
    db_session.add(onward)
    
    bag = Bag(
        id=str(uuid.UUID(int=3)),
        bag_tag="EK123",
        journey_id=journey.id,
        current_status_code="at_risk"
    )
    db_session.add(bag)
    
    event = BagEvent(
        id=str(uuid.UUID(int=4)),
        bag_id=bag.id,
        source_event_key="TEST-001",
        source_system="flight_ops",
        event_type="transfer_pending",
        event_station="DXB",
        observed_at=now,
        ingested_at=now,
        fact_type="derived",
        freshness_state="fresh",
        confidence_score=Decimal("0.75"),
        payload_json=json.dumps({})
    )
    db_session.add(event)
    
    # Test critical severity
    case_critical = ExceptionCase(
        id=str(uuid.UUID(int=5)),
        case_reference="CASE-CRITICAL",
        exception_type="short_connection_risk",
        severity_code="critical",
        deadline_at=now + timedelta(minutes=60),
        status_code="open",
        observed_state_summary="Test",
        predicted_state_summary="Test",
        created_by_user_id=str(uuid.UUID(int=1))
    )
    db_session.add(case_critical)
    db_session.commit()
    
    service = RiskAssessmentService(db_session)
    result = service.calculate_connection_risk(bag, case_critical, event)
    
    # Critical severity should result in urgency rank 1
    assert result["urgency_rank"] == 1


def test_freshness_calculation(db_session: Session):
    """Test freshness state calculation."""
    from app.repositories.bag_repository import BagEventRepository
    
    now = datetime.now(timezone.utc)
    
    # Fresh event (< 10 min)
    fresh_event = BagEvent(
        id=str(uuid.UUID(int=1)),
        bag_id=str(uuid.UUID(int=100)),
        source_event_key="TEST-FRESH",
        source_system="Wasla",
        event_type="acceptance",
        event_station="DXB",
        observed_at=now - timedelta(minutes=5),
        ingested_at=now - timedelta(minutes=5),
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=Decimal("1.00"),
        payload_json=json.dumps({})
    )
    
    # Stale event (>= 10 min)
    stale_event = BagEvent(
        id=str(uuid.UUID(int=2)),
        bag_id=str(uuid.UUID(int=100)),
        source_event_key="TEST-STALE",
        source_system="Wasla",
        event_type="loaded",
        event_station="DXB",
        observed_at=now - timedelta(minutes=20),
        ingested_at=now - timedelta(minutes=20),
        fact_type="observed",
        freshness_state="stale",
        confidence_score=Decimal("1.00"),
        payload_json=json.dumps({})
    )
    
    # Awaiting confirmation (derived/estimated)
    awaiting_event = BagEvent(
        id=str(uuid.UUID(int=3)),
        bag_id=str(uuid.UUID(int=100)),
        source_event_key="TEST-AWAITING",
        source_system="flight_ops",
        event_type="transfer_pending",
        event_station="DXB",
        observed_at=now - timedelta(minutes=5),
        ingested_at=now - timedelta(minutes=5),
        fact_type="derived",
        freshness_state="awaiting_confirmation",
        confidence_score=Decimal("0.75"),
        payload_json=json.dumps({})
    )
    
    repo = BagEventRepository(db_session)
    
    fresh_state = repo.calculate_freshness_state(fresh_event)
    assert fresh_state == "fresh"
    
    stale_state = repo.calculate_freshness_state(stale_event)
    assert stale_state == "stale"
    
    awaiting_state = repo.calculate_freshness_state(awaiting_event)
    assert awaiting_state == "awaiting_confirmation"


def test_evaluate_risk_integration(db_session: Session):
    """Test evaluate_risk method integration."""
    # Create full scenario
    journey = PassengerJourney(
        id=str(uuid.UUID(int=1)),
        passenger_reference="PAX-001",
        pnr_reference="PNR001",
        itinerary_status="active"
    )
    db_session.add(journey)
    
    now = datetime.now(timezone.utc)
    onward = JourneyLeg(
        id=str(uuid.UUID(int=2)),
        journey_id=journey.id,
        sequence_number=1,
        flight_number="EK101",
        departure_station="DXB",
        arrival_station="SYD",
        scheduled_departure_at=now + timedelta(hours=2),
        scheduled_arrival_at=now + timedelta(hours=14),
        leg_status="scheduled"
    )
    db_session.add(onward)
    
    bag = Bag(
        id=str(uuid.UUID(int=3)),
        bag_tag="EK123",
        journey_id=journey.id,
        current_status_code="in_transfer"
    )
    db_session.add(bag)
    
    event = BagEvent(
        id=str(uuid.UUID(int=4)),
        bag_id=bag.id,
        source_event_key="TEST-001",
        source_system="BRS",
        event_type="arrived",
        event_station="DXB",
        observed_at=now - timedelta(minutes=10),
        ingested_at=now - timedelta(minutes=10),
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=Decimal("1.00"),
        payload_json=json.dumps({})
    )
    db_session.add(event)
    
    case = ExceptionCase(
        id=str(uuid.UUID(int=5)),
        case_reference="CASE-001",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=now + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test",
        predicted_state_summary="Test",
        created_by_user_id=str(uuid.UUID(int=1))
    )
    db_session.add(case)
    db_session.commit()
    
    # Test evaluate_risk method
    service = RiskAssessmentService(db_session)
    result = service.evaluate_risk(bag.id, case.id)
    
    assert "risk_label" in result
    assert "urgency_rank" in result
    assert "observed_state_summary" in result
    assert "predicted_state_summary" in result
    assert 28 <= result["time_to_cutoff_minutes"] <= 31  # Allow for execution time
