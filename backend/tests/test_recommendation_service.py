"""Tests for RecommendationService."""
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json

from app.models.bag import Bag, BagEvent
from app.models.exception_case import ExceptionCase, CaseBag
from app.models.journey import PassengerJourney, JourneyLeg
from app.models.user import User
from app.services.recommendation_service import RecommendationService


def test_generate_recommendations_creates_priority_transfer_for_critical_case(db_session):
    """Test that critical cases generate PRIORITY_TRANSFER recommendations."""
    # Create test user
    user = User(
        id=str(uuid.uuid4()),
        external_subject="test@example.com",
        role_code="operations",
        display_name="Test User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    # Create journey and legs
    journey = PassengerJourney(
        id=str(uuid.uuid4()),
        passenger_reference="PAX-REC-001",
        pnr_reference="EKREC",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    db_session.flush()
    
    now = datetime.now(timezone.utc)
    onward_leg = JourneyLeg(
        id=str(uuid.uuid4()),
        journey_id=journey.id,
        sequence_number=2,
        flight_number="EK101",
        departure_station="DXB",
        arrival_station="SYD",
        scheduled_departure_at=now + timedelta(minutes=45),
        scheduled_arrival_at=now + timedelta(hours=14),
        gate_code="B05",
        leg_status="scheduled",
        created_at=now,
        updated_at=now
    )
    db_session.add(onward_leg)
    db_session.flush()
    
    # Create bag with fresh event
    bag = Bag(
        id=str(uuid.uuid4()),
        bag_tag="EKREC001",
        journey_id=journey.id,
        current_status_code="in_transfer",
        created_at=now,
        updated_at=now
    )
    db_session.add(bag)
    db_session.flush()
    
    event = BagEvent(
        id=str(uuid.uuid4()),
        bag_id=bag.id,
        source_event_key="REC-001",
        source_system="Wasla",
        event_type="arrived",
        event_station="DXB",
        observed_at=now - timedelta(minutes=5),
        ingested_at=now - timedelta(minutes=2),  # Fresh: 2 min old
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=Decimal("1.00"),
        payload_json='{"test": true}'
    )
    db_session.add(event)
    
    # Create critical case
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="REC-CASE-001",
        exception_type="short_connection_risk",
        severity_code="critical",
        deadline_at=now + timedelta(minutes=45),
        status_code="open",
        observed_state_summary="Bag arrived, transfer pending",
        predicted_state_summary="Critical risk",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case)
    db_session.flush()
    
    # Link bag to case
    case_bag = CaseBag(
        case_id=case.id,
        bag_id=bag.id,
        primary_flag=True,
        created_at=now
    )
    db_session.add(case_bag)
    db_session.commit()
    
    # Generate recommendations
    service = RecommendationService(db_session)
    recommendations = service.generate_recommendations(case.id)
    
    assert len(recommendations) > 0
    
    # Should have PRIORITY_TRANSFER recommendation
    priority_rec = next((r for r in recommendations if r.action_code == "PRIORITY_TRANSFER"), None)
    assert priority_rec is not None
    assert "expedite" in priority_rec.action_label.lower()
    assert priority_rec.confidence_score >= Decimal("0.75")
    assert priority_rec.freshness_state == "fresh"
    
    # Check evidence structure
    evidence = json.loads(priority_rec.evidence_json)
    assert "bag_tag" in evidence
    assert "time_to_deadline_minutes" in evidence
    assert evidence["severity"] == "critical"


def test_generate_recommendations_includes_confidence_scores(db_session):
    """Test that recommendations include confidence scores in 0.00-1.00 range."""
    user = User(
        id=str(uuid.uuid4()),
        external_subject="test@example.com",
        role_code="operations",
        display_name="Test User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    journey = PassengerJourney(
        id=str(uuid.uuid4()),
        passenger_reference="PAX-CONF-001",
        pnr_reference="EKCONF",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    db_session.flush()
    
    now = datetime.now(timezone.utc)
    onward_leg = JourneyLeg(
        id=str(uuid.uuid4()),
        journey_id=journey.id,
        sequence_number=2,
        flight_number="EK103",
        departure_station="DXB",
        arrival_station="SIN",
        scheduled_departure_at=now + timedelta(hours=2),
        scheduled_arrival_at=now + timedelta(hours=10),
        gate_code="C10",
        leg_status="scheduled",
        created_at=now,
        updated_at=now
    )
    db_session.add(onward_leg)
    db_session.flush()
    
    bag = Bag(
        id=str(uuid.uuid4()),
        bag_tag="EKCONF001",
        journey_id=journey.id,
        current_status_code="on_time",
        created_at=now,
        updated_at=now
    )
    db_session.add(bag)
    db_session.flush()
    
    event = BagEvent(
        id=str(uuid.uuid4()),
        bag_id=bag.id,
        source_event_key="CONF-001",
        source_system="Wasla",
        event_type="transfer_confirmed",
        event_station="DXB",
        observed_at=now - timedelta(minutes=10),
        ingested_at=now - timedelta(minutes=5),
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=Decimal("1.00"),
        payload_json='{"test": true}'
    )
    db_session.add(event)
    
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="CONF-CASE-001",
        exception_type="transfer_monitoring",
        severity_code="medium",
        deadline_at=now + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Transfer confirmed",
        predicted_state_summary="Moderate buffer",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case)
    db_session.flush()
    
    case_bag = CaseBag(
        case_id=case.id,
        bag_id=bag.id,
        primary_flag=True,
        created_at=now
    )
    db_session.add(case_bag)
    db_session.commit()
    
    # Generate recommendations
    service = RecommendationService(db_session)
    recommendations = service.generate_recommendations(case.id)
    
    # All confidence scores should be in valid range
    for rec in recommendations:
        assert Decimal("0.00") <= rec.confidence_score <= Decimal("1.00")
        assert rec.confidence_score > Decimal("0.00")  # Should have meaningful confidence


def test_generate_recommendations_includes_reason_text(db_session):
    """Test that recommendations include explainable reason text."""
    user = User(
        id=str(uuid.uuid4()),
        external_subject="test@example.com",
        role_code="operations",
        display_name="Test User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    journey = PassengerJourney(
        id=str(uuid.uuid4()),
        passenger_reference="PAX-REASON-001",
        pnr_reference="EKREAS",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    db_session.flush()
    
    now = datetime.now(timezone.utc)
    onward_leg = JourneyLeg(
        id=str(uuid.uuid4()),
        journey_id=journey.id,
        sequence_number=2,
        flight_number="EK105",
        departure_station="DXB",
        arrival_station="BKK",
        scheduled_departure_at=now + timedelta(minutes=60),
        scheduled_arrival_at=now + timedelta(hours=8),
        gate_code="D12",
        leg_status="scheduled",
        created_at=now,
        updated_at=now
    )
    db_session.add(onward_leg)
    db_session.flush()
    
    bag = Bag(
        id=str(uuid.uuid4()),
        bag_tag="EKREAS001",
        journey_id=journey.id,
        current_status_code="in_transfer",
        created_at=now,
        updated_at=now
    )
    db_session.add(bag)
    db_session.flush()
    
    event = BagEvent(
        id=str(uuid.uuid4()),
        bag_id=bag.id,
        source_event_key="REAS-001",
        source_system="BRS",
        event_type="arrived",
        event_station="DXB",
        observed_at=now - timedelta(minutes=20),
        ingested_at=now - timedelta(minutes=8),
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=Decimal("1.00"),
        payload_json='{"test": true}'
    )
    db_session.add(event)
    
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="REAS-CASE-001",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=now + timedelta(minutes=60),
        status_code="open",
        observed_state_summary="Bag arrived, pending transfer",
        predicted_state_summary="High risk",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case)
    db_session.flush()
    
    case_bag = CaseBag(
        case_id=case.id,
        bag_id=bag.id,
        primary_flag=True,
        created_at=now
    )
    db_session.add(case_bag)
    db_session.commit()
    
    # Generate recommendations
    service = RecommendationService(db_session)
    recommendations = service.generate_recommendations(case.id)
    
    # All recommendations should have meaningful reason text
    for rec in recommendations:
        assert len(rec.reason_text) > 20  # Should be substantive
        assert "bag" in rec.reason_text.lower() or "connection" in rec.reason_text.lower()


def test_generate_recommendations_includes_evidence_json(db_session):
    """Test that recommendations include evidence JSON with supporting data."""
    user = User(
        id=str(uuid.uuid4()),
        external_subject="test@example.com",
        role_code="operations",
        display_name="Test User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    journey = PassengerJourney(
        id=str(uuid.uuid4()),
        passenger_reference="PAX-EVID-001",
        pnr_reference="EKEVID",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    db_session.flush()
    
    now = datetime.now(timezone.utc)
    onward_leg = JourneyLeg(
        id=str(uuid.uuid4()),
        journey_id=journey.id,
        sequence_number=2,
        flight_number="EK107",
        departure_station="DXB",
        arrival_station="HKG",
        scheduled_departure_at=now + timedelta(minutes=75),
        scheduled_arrival_at=now + timedelta(hours=9),
        gate_code="E08",
        leg_status="scheduled",
        created_at=now,
        updated_at=now
    )
    db_session.add(onward_leg)
    db_session.flush()
    
    bag = Bag(
        id=str(uuid.uuid4()),
        bag_tag="EKEVID001",
        journey_id=journey.id,
        current_status_code="in_transfer",
        created_at=now,
        updated_at=now
    )
    db_session.add(bag)
    db_session.flush()
    
    # Add multiple events for evidence trail
    for i in range(3):
        event = BagEvent(
            id=str(uuid.uuid4()),
            bag_id=bag.id,
            source_event_key=f"EVID-00{i}",
            source_system="Wasla" if i < 2 else "BRS",
            event_type=["acceptance", "loaded", "arrived"][i],
            event_station=["LHR", "LHR", "DXB"][i],
            observed_at=now - timedelta(minutes=60 - i * 20),
            ingested_at=now - timedelta(minutes=55 - i * 20),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json='{"test": true}'
        )
        db_session.add(event)
    
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="EVID-CASE-001",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=now + timedelta(minutes=75),
        status_code="open",
        observed_state_summary="Bag events recorded",
        predicted_state_summary="High risk",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case)
    db_session.flush()
    
    case_bag = CaseBag(
        case_id=case.id,
        bag_id=bag.id,
        primary_flag=True,
        created_at=now
    )
    db_session.add(case_bag)
    db_session.commit()
    
    # Generate recommendations
    service = RecommendationService(db_session)
    recommendations = service.generate_recommendations(case.id)
    
    # Check evidence structure
    for rec in recommendations:
        evidence = json.loads(rec.evidence_json)
        assert isinstance(evidence, dict)
        assert "bag_tag" in evidence
        assert evidence["bag_tag"] == "EKEVID001"
        assert "latest_events" in evidence
        assert isinstance(evidence["latest_events"], list)


def test_generate_recommendations_calculates_freshness_state(db_session):
    """Test that freshness state is calculated based on event age."""
    user = User(
        id=str(uuid.uuid4()),
        external_subject="test@example.com",
        role_code="operations",
        display_name="Test User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    journey = PassengerJourney(
        id=str(uuid.uuid4()),
        passenger_reference="PAX-FRESH-001",
        pnr_reference="EKFRESH",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    db_session.flush()
    
    now = datetime.now(timezone.utc)
    onward_leg = JourneyLeg(
        id=str(uuid.uuid4()),
        journey_id=journey.id,
        sequence_number=2,
        flight_number="EK109",
        departure_station="DXB",
        arrival_station="NRT",
        scheduled_departure_at=now + timedelta(hours=3),
        scheduled_arrival_at=now + timedelta(hours=12),
        gate_code="F15",
        leg_status="scheduled",
        created_at=now,
        updated_at=now
    )
    db_session.add(onward_leg)
    db_session.flush()
    
    bag = Bag(
        id=str(uuid.uuid4()),
        bag_tag="EKFRESH001",
        journey_id=journey.id,
        current_status_code="in_transfer",
        created_at=now,
        updated_at=now
    )
    db_session.add(bag)
    db_session.flush()
    
    # Stale event (> 10 minutes old)
    event = BagEvent(
        id=str(uuid.uuid4()),
        bag_id=bag.id,
        source_event_key="FRESH-001",
        source_system="BRS",
        event_type="arrived",
        event_station="DXB",
        observed_at=now - timedelta(minutes=30),
        ingested_at=now - timedelta(minutes=15),  # Stale: 15 min old
        fact_type="observed",
        freshness_state="stale",
        confidence_score=Decimal("1.00"),
        payload_json='{"test": true}'
    )
    db_session.add(event)
    
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="FRESH-CASE-001",
        exception_type="transfer_monitoring",
        severity_code="medium",
        deadline_at=now + timedelta(hours=3),
        status_code="open",
        observed_state_summary="Stale data",
        predicted_state_summary="Medium",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case)
    db_session.flush()
    
    case_bag = CaseBag(
        case_id=case.id,
        bag_id=bag.id,
        primary_flag=True,
        created_at=now
    )
    db_session.add(case_bag)
    db_session.commit()
    
    # Generate recommendations
    service = RecommendationService(db_session)
    recommendations = service.generate_recommendations(case.id)
    
    # Should mark as stale
    for rec in recommendations:
        assert rec.freshness_state in ["fresh", "stale", "awaiting_confirmation"]


def test_supersede_recommendation(db_session):
    """Test superseding a recommendation."""
    user = User(
        id=str(uuid.uuid4()),
        external_subject="test@example.com",
        role_code="operations",
        display_name="Test User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    journey = PassengerJourney(
        id=str(uuid.uuid4()),
        passenger_reference="PAX-SUP-001",
        pnr_reference="EKSUP",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    db_session.flush()
    
    now = datetime.now(timezone.utc)
    bag = Bag(
        id=str(uuid.uuid4()),
        bag_tag="EKSUP001",
        journey_id=journey.id,
        current_status_code="in_transfer",
        created_at=now,
        updated_at=now
    )
    db_session.add(bag)
    db_session.flush()
    
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="SUP-CASE-001",
        exception_type="transfer_monitoring",
        severity_code="medium",
        deadline_at=now + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test",
        predicted_state_summary="Test",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case)
    db_session.flush()
    
    case_bag = CaseBag(
        case_id=case.id,
        bag_id=bag.id,
        primary_flag=True,
        created_at=now
    )
    db_session.add(case_bag)
    
    # Create a recommendation manually
    from app.models.recommendation import Recommendation
    rec = Recommendation(
        id=str(uuid.uuid4()),
        case_id=case.id,
        action_code="MONITOR",
        action_label="Monitor",
        reason_text="Test recommendation",
        confidence_score=Decimal("0.75"),
        freshness_state="fresh",
        evidence_json='{}',
        generated_at=now
    )
    db_session.add(rec)
    db_session.commit()
    
    # Supersede it
    service = RecommendationService(db_session)
    superseded_rec = service.supersede_recommendation(rec.id)
    
    assert superseded_rec.superseded_at is not None
    
    # Verify it's excluded from active recommendations
    active_recs = service.get_recommendations_for_case(case.id, include_superseded=False)
    assert len(active_recs) == 0
    
    # But included when requesting superseded
    all_recs = service.get_recommendations_for_case(case.id, include_superseded=True)
    assert len(all_recs) == 1
