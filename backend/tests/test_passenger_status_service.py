"""Tests for passenger status service case status composition."""
import json
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models.bag import Bag, BagEvent
from app.models.exception_case import CaseBag, ExceptionCase
from app.models.journey import JourneyLeg, PassengerJourney
from app.models.passenger_view import PassengerCaseView
from app.models.user import User
from app.services.passenger_status_service import PassengerStatusService


def test_compose_case_status_returns_confirmed_and_estimated_steps(db_session):
    """Test case status composition includes confirmed and estimated progress steps."""
    # Arrange: Create user, journey, bag, case, and passenger view
    user = User(
        id=str(uuid.uuid4()),
        external_subject="ops@test",
        role_code="operations",
        display_name="Ops User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    journey = PassengerJourney(
        id=str(uuid.uuid4()),
        passenger_reference="PASS-001",
        pnr_reference="PNR001",
        itinerary_status="confirmed",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    
    now = datetime.now(timezone.utc)
    bag = Bag(
        id=str(uuid.uuid4()),
        bag_tag="TEST001",
        journey_id=journey.id,
        current_status_code="exception",
        created_at=now,
        updated_at=now
    )
    db_session.add(bag)
    
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="BC-TEST-001",
        exception_type="short_connection_risk",
        severity_code="critical",
        deadline_at=now + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Bag arrived, transfer scan missing",
        predicted_state_summary="Critical priority required",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case)
    
    bag.current_case_id = case.id
    
    case_bag = CaseBag(
        case_id=case.id,
        bag_id=bag.id,
        primary_flag=True,
        created_at=now
    )
    db_session.add(case_bag)
    
    # Create passenger view with both confirmed and estimated steps
    passenger_view = PassengerCaseView(
        id=str(uuid.uuid4()),
        case_id=case.id,
        case_reference="BC-TEST-001",
        latest_confirmed_status="Arrived at Dubai 10:30 GST",
        estimated_notice="Being prioritised for onward flight. Estimated delivery within 60 minutes",
        next_expected_update="2 hours before departure",
        passenger_safe_payload_json=json.dumps({
            "progress_steps": [
                {
                    "step_text": "Arrived at Dubai 10:30 GST",
                    "status": "confirmed",
                    "timestamp": (now - timedelta(hours=1)).isoformat()
                },
                {
                    "step_text": "Being prioritised for onward flight",
                    "status": "estimated",
                    "timestamp": None,
                    "uncertainty_note": "Estimated based on current operational priority"
                }
            ],
            "case_status": "open",
            "severity": "critical"
        }),
        refreshed_at=now
    )
    db_session.add(passenger_view)
    db_session.commit()
    
    # Act: Compose case status
    service = PassengerStatusService(db_session)
    result = service.compose_case_status_for_passenger("BC-TEST-001")
    
    # Assert: Verify response structure
    assert result is not None
    assert result.case_reference == "BC-TEST-001"
    assert result.latest_confirmed_status == "Arrived at Dubai 10:30 GST"
    assert result.estimated_notice == "Being prioritised for onward flight. Estimated delivery within 60 minutes"
    assert result.next_expected_update == "2 hours before departure"
    assert len(result.progress_steps) == 2
    
    # Assert: Verify confirmed step
    confirmed_step = result.progress_steps[0]
    assert confirmed_step.step_text == "Arrived at Dubai 10:30 GST"
    assert confirmed_step.status == "confirmed"
    assert confirmed_step.timestamp is not None
    
    # Assert: Verify estimated step with uncertainty note
    estimated_step = result.progress_steps[1]
    assert estimated_step.step_text == "Being prioritised for onward flight"
    assert estimated_step.status == "estimated"
    assert estimated_step.timestamp is None
    assert estimated_step.uncertainty_note == "Estimated based on current operational priority"


def test_compose_case_status_excludes_internal_notes(db_session):
    """Test case status excludes internal operational notes and risk scores."""
    # Arrange
    user = User(
        id=str(uuid.uuid4()),
        external_subject="ops@test",
        role_code="operations",
        display_name="Ops User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    now = datetime.now(timezone.utc)
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="BC-TEST-002",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=now + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Internal operational notes: handler delay, risk score 0.85",
        predicted_state_summary="High risk of missed connection, alternative recommendation superseded",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case)
    
    # Passenger view excludes internal notes
    passenger_view = PassengerCaseView(
        id=str(uuid.uuid4()),
        case_id=case.id,
        case_reference="BC-TEST-002",
        latest_confirmed_status="Baggage in recovery process",
        estimated_notice="Being monitored for timely transfer",
        next_expected_update="90 minutes before departure",
        passenger_safe_payload_json=json.dumps({
            "progress_steps": [
                {
                    "step_text": "Baggage in recovery process",
                    "status": "confirmed",
                    "timestamp": now.isoformat()
                }
            ],
            "case_status": "open",
            "severity": "high"
        }),
        refreshed_at=now
    )
    db_session.add(passenger_view)
    db_session.commit()
    
    # Act
    service = PassengerStatusService(db_session)
    result = service.compose_case_status_for_passenger("BC-TEST-002")
    
    # Assert: Verify internal notes are excluded
    assert result is not None
    assert "risk score" not in result.latest_confirmed_status.lower()
    assert "handler delay" not in result.latest_confirmed_status.lower()
    assert "alternative recommendation" not in str(result.estimated_notice or "").lower()
    # Progress steps should not contain internal operational detail
    for step in result.progress_steps:
        assert "risk score" not in step.step_text.lower()
        assert "handler delay" not in step.step_text.lower()


def test_compose_case_status_returns_404_for_unauthorized_reference(db_session):
    """Test case status returns None (404) for unauthorized case references."""
    # Arrange: No passenger view exists for this reference
    service = PassengerStatusService(db_session)
    
    # Act: Request non-existent case reference
    result = service.compose_case_status_for_passenger("BC-UNAUTHORIZED-999")
    
    # Assert: Returns None to signal 404 (prevents information leakage)
    assert result is None


def test_compose_case_status_handles_closed_case_with_confirmed_delivery(db_session):
    """Test case status for closed case shows confirmed delivery without estimated notice."""
    # Arrange
    user = User(
        id=str(uuid.uuid4()),
        external_subject="ops@test",
        role_code="operations",
        display_name="Ops User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    now = datetime.now(timezone.utc)
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="BC-TEST-003",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=now + timedelta(hours=2),
        status_code="closed",
        observed_state_summary="Delivered to belt 5",
        predicted_state_summary="Case resolved",
        created_by_user_id=user.id,
        created_at=now - timedelta(hours=2),
        updated_at=now - timedelta(minutes=10),
        closed_at=now - timedelta(minutes=10)
    )
    db_session.add(case)
    
    # Passenger view for closed case
    passenger_view = PassengerCaseView(
        id=str(uuid.uuid4()),
        case_id=case.id,
        case_reference="BC-TEST-003",
        latest_confirmed_status="Delivered to belt 5",
        estimated_notice=None,  # No estimated notice for closed cases
        next_expected_update="Case resolved",
        passenger_safe_payload_json=json.dumps({
            "progress_steps": [
                {
                    "step_text": "Arrived at Dubai 09:00 GST",
                    "status": "confirmed",
                    "timestamp": (now - timedelta(hours=2)).isoformat()
                },
                {
                    "step_text": "Delivered to belt 5",
                    "status": "confirmed",
                    "timestamp": (now - timedelta(minutes=10)).isoformat()
                }
            ],
            "case_status": "closed",
            "severity": "high"
        }),
        refreshed_at=now
    )
    db_session.add(passenger_view)
    db_session.commit()
    
    # Act
    service = PassengerStatusService(db_session)
    result = service.compose_case_status_for_passenger("BC-TEST-003")
    
    # Assert: Closed case has no estimated notice
    assert result is not None
    assert result.latest_confirmed_status == "Delivered to belt 5"
    assert result.estimated_notice is None
    assert result.next_expected_update == "Case resolved"
    # All steps should be confirmed
    for step in result.progress_steps:
        assert step.status == "confirmed"
        assert step.timestamp is not None


def test_refresh_passenger_view_creates_new_view_idempotently(db_session):
    """Test refresh_passenger_view creates new view when none exists."""
    # Arrange
    user = User(
        id=str(uuid.uuid4()),
        external_subject="ops@test",
        role_code="operations",
        display_name="Ops User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    journey = PassengerJourney(
        id=str(uuid.uuid4()),
        passenger_reference="PASS-002",
        pnr_reference="PNR002",
        itinerary_status="confirmed",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    
    now = datetime.now(timezone.utc)
    bag = Bag(
        id=str(uuid.uuid4()),
        bag_tag="TEST002",
        journey_id=journey.id,
        current_status_code="exception",
        created_at=now,
        updated_at=now
    )
    db_session.add(bag)
    
    # Create bag arrival event
    arrival_event = BagEvent(
        id=str(uuid.uuid4()),
        bag_id=bag.id,
        source_event_key="TEST-002-ARR",
        source_system="BHS",
        event_type="arrived",
        event_station="DXB",
        observed_at=now - timedelta(hours=1),
        ingested_at=now - timedelta(hours=1),
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=1.0,
        payload_json=json.dumps({"event": "arrival"})
    )
    db_session.add(arrival_event)
    
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="BC-TEST-004",
        exception_type="short_connection_risk",
        severity_code="critical",
        deadline_at=now + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Bag arrived, transfer scan missing",
        predicted_state_summary="Critical priority",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case)
    
    bag.current_case_id = case.id
    
    case_bag = CaseBag(
        case_id=case.id,
        bag_id=bag.id,
        primary_flag=True,
        created_at=now
    )
    db_session.add(case_bag)
    db_session.commit()
    
    # Act: Refresh passenger view (should create new one)
    service = PassengerStatusService(db_session)
    result = service.refresh_passenger_view(case.id)
    
    # Assert: New view created
    assert result is not None
    assert result.case_id == case.id
    assert result.case_reference == "BC-TEST-004"
    assert result.latest_confirmed_status is not None
    assert result.refreshed_at is not None
    
    # Verify idempotency: calling again should update existing view
    first_refreshed_at = result.refreshed_at
    result2 = service.refresh_passenger_view(case.id)
    assert result2.id == result.id
    assert result2.refreshed_at >= first_refreshed_at


def test_refresh_passenger_view_updates_existing_view(db_session):
    """Test refresh_passenger_view updates existing view idempotently."""
    # Arrange
    user = User(
        id=str(uuid.uuid4()),
        external_subject="ops@test",
        role_code="operations",
        display_name="Ops User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    journey = PassengerJourney(
        id=str(uuid.uuid4()),
        passenger_reference="PASS-003",
        pnr_reference="PNR003",
        itinerary_status="confirmed",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    
    now = datetime.now(timezone.utc)
    bag = Bag(
        id=str(uuid.uuid4()),
        bag_tag="TEST003",
        journey_id=journey.id,
        current_status_code="exception",
        created_at=now,
        updated_at=now
    )
    db_session.add(bag)
    
    arrival_event = BagEvent(
        id=str(uuid.uuid4()),
        bag_id=bag.id,
        source_event_key="TEST-003-ARR",
        source_system="BHS",
        event_type="arrived",
        event_station="DXB",
        observed_at=now - timedelta(hours=1),
        ingested_at=now - timedelta(hours=1),
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=1.0,
        payload_json=json.dumps({"event": "arrival"})
    )
    db_session.add(arrival_event)
    
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="BC-TEST-005",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=now + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Bag arrived",
        predicted_state_summary="High priority",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case)
    
    bag.current_case_id = case.id
    
    case_bag = CaseBag(
        case_id=case.id,
        bag_id=bag.id,
        primary_flag=True,
        created_at=now
    )
    db_session.add(case_bag)
    
    # Create existing passenger view
    old_view = PassengerCaseView(
        id=str(uuid.uuid4()),
        case_id=case.id,
        case_reference="BC-TEST-005",
        latest_confirmed_status="Old status",
        estimated_notice="Old notice",
        next_expected_update="Old update",
        passenger_safe_payload_json=json.dumps({"old": "data"}),
        refreshed_at=now - timedelta(hours=1)
    )
    db_session.add(old_view)
    db_session.commit()
    
    old_view_id = old_view.id
    old_refreshed = old_view.refreshed_at
    
    # Act: Refresh should update existing view
    service = PassengerStatusService(db_session)
    result = service.refresh_passenger_view(case.id)
    
    # Assert: Same view updated
    assert result is not None
    assert result.id == old_view_id
    assert result.latest_confirmed_status != "Old status"
    assert result.refreshed_at > old_refreshed


def test_refresh_passenger_view_returns_none_for_nonexistent_case(db_session):
    """Test refresh_passenger_view returns None for non-existent case."""
    # Arrange
    service = PassengerStatusService(db_session)
    
    # Act: Refresh non-existent case
    result = service.refresh_passenger_view(str(uuid.uuid4()))
    
    # Assert
    assert result is None
