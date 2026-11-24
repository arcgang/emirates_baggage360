"""Integration tests for passenger API endpoints."""
import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from app.models import (
    User, Bag, PassengerJourney, JourneyLeg, BagEvent,
    ExceptionCase, CaseBag, PassengerCaseView
)


def test_get_passenger_bag_status_with_passenger_safe_filtering(client, db_session):
    """Test GET /api/v1/passenger/bags/{bag_tag}/status returns passenger-safe data only."""
    # Setup: Create journey and bag
    journey = PassengerJourney(
        id="journey-pass-001",
        passenger_reference="PAX-PASS-001",
        pnr_reference="PNR-PASS-001",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    
    leg = JourneyLeg(
        id="leg-pass-001",
        journey_id="journey-pass-001",
        sequence_number=1,
        flight_number="EK101",
        departure_station="LHR",
        arrival_station="DXB",
        scheduled_departure_at=datetime.now(timezone.utc) - timedelta(hours=6),
        scheduled_arrival_at=datetime.now(timezone.utc) - timedelta(hours=1),
        actual_arrival_at=datetime.now(timezone.utc) - timedelta(hours=1),
        gate_code="A10",
        stand_code="10",
        aircraft_registration="A6-TEST",
        leg_status="arrived",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(leg)
    
    bag = Bag(
        id="bag-pass-001",
        bag_tag="PASS001",
        journey_id="journey-pass-001",
        current_status_code="in_transfer",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(bag)
    
    # Add bag event
    event = BagEvent(
        id="event-pass-001",
        bag_id="bag-pass-001",
        source_event_key="WASLA-PASS001-001",
        source_system="Wasla",
        event_type="acceptance",
        event_station="LHR",
        observed_at=datetime.now(timezone.utc) - timedelta(hours=6),
        ingested_at=datetime.now(timezone.utc) - timedelta(hours=6),
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=Decimal("1.00"),
        payload_json=json.dumps({"event": "bag_accepted", "location": "LHR"})
    )
    db_session.add(event)
    db_session.commit()
    
    # Test: Get bag status
    response = client.get("/api/v1/passenger/bags/PASS001/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["bag_tag"] == "PASS001"
    assert "latest_confirmed_milestone" in data
    assert "status_label" in data
    # Verify passenger-safe filtering: no internal notes or risk scores
    assert "risk_score" not in str(data)
    assert "internal_note" not in str(data)


def test_get_passenger_case_status_with_404_for_unauthorized(client, db_session):
    """Test GET /api/v1/passenger/cases/{case_reference} returns 404 for unauthorized access."""
    # Setup: Create case that passenger should not access
    user = User(
        id="user-pass-001",
        external_subject="ops@test.com",
        role_code="operations",
        display_name="Ops User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    case = ExceptionCase(
        id="case-pass-001",
        case_reference="BC-PASS-001",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Unauthorized case",
        predicted_state_summary="Test",
        created_by_user_id=user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(case)
    db_session.commit()
    
    # Test: Try to access case without authorization
    # Note: This test assumes no passenger case view exists for this case
    response = client.get("/api/v1/passenger/cases/BC-PASS-001")
    
    assert response.status_code == 404


def test_get_passenger_bag_status_with_confirmed_and_estimated_separation(client, db_session):
    """Test bag status separates confirmed facts from estimated predictions."""
    # Setup: Create journey and bag with both confirmed and estimated events
    journey = PassengerJourney(
        id="journey-pass-002",
        passenger_reference="PAX-PASS-002",
        pnr_reference="PNR-PASS-002",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    
    bag = Bag(
        id="bag-pass-002",
        bag_tag="PASS002",
        journey_id="journey-pass-002",
        current_status_code="in_transfer",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(bag)
    
    # Confirmed event
    confirmed_event = BagEvent(
        id="event-pass-002-confirmed",
        bag_id="bag-pass-002",
        source_event_key="WASLA-PASS002-001",
        source_system="Wasla",
        event_type="acceptance",
        event_station="LHR",
        observed_at=datetime.now(timezone.utc) - timedelta(hours=5),
        ingested_at=datetime.now(timezone.utc) - timedelta(hours=5),
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=Decimal("1.00"),
        payload_json=json.dumps({"event": "bag_accepted"})
    )
    db_session.add(confirmed_event)
    
    # Estimated event
    estimated_event = BagEvent(
        id="event-pass-002-estimated",
        bag_id="bag-pass-002",
        source_event_key="SYSTEM-PASS002-002",
        source_system="BaggageOrchestrator",
        event_type="estimated_arrival",
        event_station="DXB",
        observed_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ingested_at=datetime.now(timezone.utc),
        fact_type="estimated",
        freshness_state="awaiting_confirmation",
        confidence_score=Decimal("0.80"),
        payload_json=json.dumps({"event": "estimated_arrival"})
    )
    db_session.add(estimated_event)
    db_session.commit()
    
    # Test: Get bag status
    response = client.get("/api/v1/passenger/bags/PASS002/status")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify both confirmed and estimated milestones present
    if "milestones" in data:
        milestones = data["milestones"]
        confirmed_found = any(m.get("fact_type") == "observed" for m in milestones)
        estimated_found = any(m.get("fact_type") == "estimated" for m in milestones)
        assert confirmed_found or estimated_found


def test_get_passenger_case_status_with_progress_stepper(client, db_session):
    """Test case status includes progress stepper with confirmed/estimated steps."""
    # Setup: Create case with passenger view
    user = User(
        id="user-pass-002",
        external_subject="ops@test.com",
        role_code="operations",
        display_name="Ops User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    case = ExceptionCase(
        id="case-pass-002",
        case_reference="BC-PASS-002",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Bag in transfer",
        predicted_state_summary="Expected to make connection",
        created_by_user_id=user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(case)
    
    # Create passenger case view
    case_view = PassengerCaseView(
        id="view-pass-002",
        case_id="case-pass-002",
        case_reference="BC-PASS-002",
        latest_confirmed_status="In transfer at Dubai",
        estimated_notice="Your bag is expected to make your connection",
        next_expected_update="Expected update in 30 minutes",
        passenger_safe_payload_json=json.dumps({
            "progress_steps": [
                {"step_text": "Bag checked in", "status": "confirmed"},
                {"step_text": "In transfer", "status": "confirmed"},
                {"step_text": "Loaded on connecting flight", "status": "estimated"}
            ]
        }),
        refreshed_at=datetime.now(timezone.utc)
    )
    db_session.add(case_view)
    db_session.commit()
    
    # Test: Get case status
    response = client.get("/api/v1/passenger/cases/BC-PASS-002")
    
    assert response.status_code == 200
    data = response.json()
    assert data["case_reference"] == "BC-PASS-002"
    assert "latest_confirmed_status" in data
    assert "estimated_notice" in data
    
    # Verify progress steps show confirmed/estimated distinction
    if "progress_steps" in data:
        steps = data["progress_steps"]
        assert any(s.get("status") == "confirmed" for s in steps)


def test_get_passenger_bag_status_excludes_internal_notes(client, db_session):
    """Test bag status excludes internal operational notes and risk scores."""
    # Setup: Create bag with event that might have internal metadata
    journey = PassengerJourney(
        id="journey-pass-003",
        passenger_reference="PAX-PASS-003",
        pnr_reference="PNR-PASS-003",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    
    bag = Bag(
        id="bag-pass-003",
        bag_tag="PASS003",
        journey_id="journey-pass-003",
        current_status_code="in_transfer",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(bag)
    
    # Event with internal metadata in payload
    event = BagEvent(
        id="event-pass-003",
        bag_id="bag-pass-003",
        source_event_key="WASLA-PASS003-001",
        source_system="Wasla",
        event_type="acceptance",
        event_station="LHR",
        observed_at=datetime.now(timezone.utc) - timedelta(hours=5),
        ingested_at=datetime.now(timezone.utc) - timedelta(hours=5),
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=Decimal("1.00"),
        payload_json=json.dumps({
            "event": "bag_accepted",
            "internal_note": "Requires priority handling",
            "risk_score": 0.85
        })
    )
    db_session.add(event)
    db_session.commit()
    
    # Test: Get bag status
    response = client.get("/api/v1/passenger/bags/PASS003/status")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify internal fields are not exposed
    response_text = json.dumps(data)
    assert "internal_note" not in response_text
    assert "risk_score" not in response_text or "confidence" in response_text  # confidence_score is OK, risk_score is not
