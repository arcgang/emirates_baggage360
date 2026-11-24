"""Tests for ExceptionCaseService."""
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.bag import Bag, BagEvent
from app.models.exception_case import ExceptionCase
from app.models.journey import PassengerJourney, JourneyLeg
from app.models.user import User
from app.services.exception_case_service import ExceptionCaseService


def test_create_case_groups_bags_with_severity(db_session):
    """Test that create_case groups bags and calculates severity."""
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
        passenger_reference="PAX-TEST-001",
        pnr_reference="EKTEST",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    db_session.flush()
    
    now = datetime.now(timezone.utc)
    inbound_leg = JourneyLeg(
        id=str(uuid.uuid4()),
        journey_id=journey.id,
        sequence_number=1,
        flight_number="EK001",
        departure_station="LHR",
        arrival_station="DXB",
        scheduled_departure_at=now - timedelta(hours=6),
        scheduled_arrival_at=now - timedelta(hours=1),
        actual_arrival_at=now - timedelta(hours=1),
        leg_status="arrived",
        created_at=now,
        updated_at=now
    )
    db_session.add(inbound_leg)
    
    onward_leg = JourneyLeg(
        id=str(uuid.uuid4()),
        journey_id=journey.id,
        sequence_number=2,
        flight_number="EK101",
        departure_station="DXB",
        arrival_station="SYD",
        scheduled_departure_at=now + timedelta(minutes=45),  # Critical: 45 min to departure
        scheduled_arrival_at=now + timedelta(hours=14),
        gate_code="B05",
        leg_status="scheduled",
        created_at=now,
        updated_at=now
    )
    db_session.add(onward_leg)
    db_session.flush()
    
    # Create bag
    bag = Bag(
        id=str(uuid.uuid4()),
        bag_tag="EKTEST001",
        journey_id=journey.id,
        current_status_code="in_transfer",
        created_at=now,
        updated_at=now
    )
    db_session.add(bag)
    
    # Create bag event
    event = BagEvent(
        id=str(uuid.uuid4()),
        bag_id=bag.id,
        source_event_key="TEST-001",
        source_system="Wasla",
        event_type="arrived",
        event_station="DXB",
        observed_at=now - timedelta(minutes=30),
        ingested_at=now - timedelta(minutes=5),
        fact_type="observed",
        freshness_state="fresh",
        confidence_score=Decimal("1.00"),
        payload_json='{"test": true}'
    )
    db_session.add(event)
    db_session.commit()
    
    # Test case creation
    service = ExceptionCaseService(db_session)
    case = service.create_case(
        bag_ids=[bag.id],
        exception_type="short_connection_risk",
        created_by_user_id=user.id
    )
    
    assert case is not None
    assert case.case_reference.startswith("BC-DXB-")
    assert case.severity_code == "critical"  # < 60 min to deadline
    assert case.status_code == "open"
    assert "arrived" in case.observed_state_summary.lower()
    assert case.created_by_user_id == user.id


def test_create_case_calculates_deadline_from_onward_flight(db_session):
    """Test that deadline is calculated as 90 minutes before onward departure."""
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
    
    # Create journey
    journey = PassengerJourney(
        id=str(uuid.uuid4()),
        passenger_reference="PAX-TEST-002",
        pnr_reference="EKTEST2",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    db_session.flush()
    
    now = datetime.now(timezone.utc)
    departure_time = now + timedelta(hours=3)  # Departure in 3 hours
    
    onward_leg = JourneyLeg(
        id=str(uuid.uuid4()),
        journey_id=journey.id,
        sequence_number=2,
        flight_number="EK101",
        departure_station="DXB",
        arrival_station="SYD",
        scheduled_departure_at=departure_time,
        scheduled_arrival_at=departure_time + timedelta(hours=14),
        leg_status="scheduled",
        created_at=now,
        updated_at=now
    )
    db_session.add(onward_leg)
    db_session.flush()
    
    # Create bag
    bag = Bag(
        id=str(uuid.uuid4()),
        bag_tag="EKTEST002",
        journey_id=journey.id,
        current_status_code="in_transfer",
        created_at=now,
        updated_at=now
    )
    db_session.add(bag)
    db_session.commit()
    
    # Create case
    service = ExceptionCaseService(db_session)
    case = service.create_case(
        bag_ids=[bag.id],
        exception_type="short_connection_risk",
        created_by_user_id=user.id
    )
    
    # Deadline should be 90 minutes before departure
    expected_deadline = departure_time - timedelta(minutes=90)
    # SQLite returns timezone-naive datetimes, so compare as naive
    if case.deadline_at.tzinfo is None and expected_deadline.tzinfo is not None:
        expected_deadline = expected_deadline.replace(tzinfo=None)
    # Allow 1 minute tolerance for test execution time
    assert abs((case.deadline_at - expected_deadline).total_seconds()) < 60


def test_list_prioritized_cases_orders_by_deadline(db_session):
    """Test that list_prioritized_cases returns cases ordered by deadline (most urgent first)."""
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
    db_session.flush()
    
    now = datetime.now(timezone.utc)
    
    # Create cases with different deadlines
    case1 = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="TEST-001",
        exception_type="short_connection_risk",
        severity_code="critical",
        deadline_at=now + timedelta(minutes=30),  # Most urgent
        status_code="open",
        observed_state_summary="Test case 1",
        predicted_state_summary="Critical",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case1)
    
    case2 = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="TEST-002",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=now + timedelta(hours=2),  # Less urgent
        status_code="open",
        observed_state_summary="Test case 2",
        predicted_state_summary="High",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case2)
    
    case3 = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="TEST-003",
        exception_type="transfer_monitoring",
        severity_code="medium",
        deadline_at=now + timedelta(hours=1),  # Middle urgency
        status_code="open",
        observed_state_summary="Test case 3",
        predicted_state_summary="Medium",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case3)
    db_session.commit()
    
    # Test prioritization
    service = ExceptionCaseService(db_session)
    cases = service.list_prioritized_cases()
    
    assert len(cases) == 3
    assert cases[0].case_reference == "TEST-001"  # Most urgent first
    assert cases[1].case_reference == "TEST-003"  # Middle
    assert cases[2].case_reference == "TEST-002"  # Least urgent


def test_list_prioritized_cases_filters_by_severity(db_session):
    """Test that severity filter works."""
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
    db_session.flush()
    
    now = datetime.now(timezone.utc)
    
    critical_case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="CRIT-001",
        exception_type="short_connection_risk",
        severity_code="critical",
        deadline_at=now + timedelta(hours=1),
        status_code="open",
        observed_state_summary="Critical case",
        predicted_state_summary="Critical",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(critical_case)
    
    medium_case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="MED-001",
        exception_type="transfer_monitoring",
        severity_code="medium",
        deadline_at=now + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Medium case",
        predicted_state_summary="Medium",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(medium_case)
    db_session.commit()
    
    service = ExceptionCaseService(db_session)
    
    # Filter by critical
    critical_cases = service.list_prioritized_cases(severity="critical")
    assert len(critical_cases) == 1
    assert critical_cases[0].severity_code == "critical"
    
    # Filter by medium
    medium_cases = service.list_prioritized_cases(severity="medium")
    assert len(medium_cases) == 1
    assert medium_cases[0].severity_code == "medium"


def test_update_case_status(db_session):
    """Test updating case status and closed_at timestamp."""
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
    db_session.flush()
    
    now = datetime.now(timezone.utc)
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="STATUS-001",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=now + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test case",
        predicted_state_summary="High",
        created_by_user_id=user.id,
        created_at=now,
        updated_at=now
    )
    db_session.add(case)
    db_session.commit()
    
    service = ExceptionCaseService(db_session)
    
    # Update to closed
    updated_case = service.update_case_status(case.id, "closed")
    assert updated_case.status_code == "closed"
    assert updated_case.closed_at is not None
    # Note: updated_at may be same if update happens within same microsecond
    assert updated_case.updated_at >= case.updated_at


def test_get_case_bag_count(db_session):
    """Test counting bags in a case."""
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
        passenger_reference="PAX-COUNT-001",
        pnr_reference="EKCOUNT",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    db_session.flush()
    
    now = datetime.now(timezone.utc)
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="COUNT-001",
        exception_type="short_connection_risk",
        severity_code="high",
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
    
    # Add 3 bags to case
    for i in range(3):
        bag = Bag(
            id=str(uuid.uuid4()),
            bag_tag=f"EKCOUNT00{i}",
            journey_id=journey.id,
            current_status_code="in_transfer",
            created_at=now,
            updated_at=now
        )
        db_session.add(bag)
        db_session.flush()
        
        from app.repositories.exception_case_repository import ExceptionCaseRepository
        repo = ExceptionCaseRepository(db_session)
        repo.add_bag_to_case(case.id, bag.id, primary_flag=(i == 0))
    
    # Test count
    from app.repositories.exception_case_repository import ExceptionCaseRepository
    repo = ExceptionCaseRepository(db_session)
    count = repo.get_case_bag_count(case.id)
    assert count == 3
