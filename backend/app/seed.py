"""Idempotent seed data for local development and demos."""
import uuid
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import bcrypt
from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from .models import (
    User, PassengerJourney, JourneyLeg, Bag, BagEvent, ExceptionCase,
    CaseBag, Recommendation, ApprovalDecision, Task, TaskEvidence,
    PassengerCaseView, ExecutiveDailyMetric, AuditEvent, SessionAccessLog
)


def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def seed_users(db: Session) -> dict[str, User]:
    """Seed demo users with known credentials."""
    users = {
        "operations": User(
            id=str(uuid.UUID(int=1)),
            external_subject="mariam.alsuwaidi@baggage360.demo",
            role_code="operations",
            display_name="Mariam Al Suwaidi",
            station_scope="DXB",
            active_flag=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        "partner": User(
            id=str(uuid.UUID(int=2)),
            external_subject="ahmed.hassan@dnata.ae",
            role_code="partner",
            display_name="Ahmed Hassan",
            partner_org_code="DNATA",
            station_scope="DXB",
            active_flag=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        "passenger": User(
            id=str(uuid.UUID(int=3)),
            external_subject="sara.johnson@example.com",
            role_code="passenger",
            display_name="Sara Johnson",
            passenger_reference="PAX-20241101-001",
            active_flag=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
        "executive": User(
            id=str(uuid.UUID(int=4)),
            external_subject="fatima.albanna@emirates.ae",
            role_code="executive",
            display_name="Fatima Al Banna",
            station_scope="DXB",
            active_flag=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        ),
    }
    
    for user_key, user in users.items():
        existing = db.query(User).filter(User.id == user.id).first()
        if not existing:
            db.add(user)
    
    db.commit()
    return users


def seed_journeys(db: Session, users: dict) -> dict[str, PassengerJourney]:
    """Seed passenger journeys."""
    journey1 = PassengerJourney(
        id=str(uuid.UUID(int=101)),
        passenger_reference="PAX-20241101-001",
        pnr_reference="EK2024ABC",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    journey2 = PassengerJourney(
        id=str(uuid.UUID(int=102)),
        passenger_reference="PAX-20241101-002",
        pnr_reference="EK2024DEF",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    journeys = {"journey1": journey1, "journey2": journey2}
    
    for journey_key, journey in journeys.items():
        existing = db.query(PassengerJourney).filter(PassengerJourney.id == journey.id).first()
        if not existing:
            db.add(journey)
    
    db.commit()
    return journeys


def seed_journey_legs(db: Session, journeys: dict) -> None:
    """Seed journey legs with varying connection windows for risk testing."""
    now = datetime.now(timezone.utc)
    
    legs = [
        # Journey 1 - Critical risk: 36 minutes to cutoff (departure in 2h6min)
        JourneyLeg(
            id=str(uuid.UUID(int=201)),
            journey_id=journeys["journey1"].id,
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
        ),
        JourneyLeg(
            id=str(uuid.UUID(int=202)),
            journey_id=journeys["journey1"].id,
            sequence_number=2,
            flight_number="EK101",
            departure_station="DXB",
            arrival_station="SYD",
            scheduled_departure_at=now + timedelta(hours=2, minutes=6),  # 36 min to cutoff
            scheduled_arrival_at=now + timedelta(hours=14),
            gate_code="B05",
            stand_code="45",
            aircraft_registration="A6-EUB",
            leg_status="scheduled",
            created_at=now,
            updated_at=now,
        ),
        # Journey 2 - Medium risk: 85 minutes to cutoff (departure in 2h55min)
        JourneyLeg(
            id=str(uuid.UUID(int=203)),
            journey_id=journeys["journey2"].id,
            sequence_number=1,
            flight_number="EK002",
            departure_station="LHR",
            arrival_station="DXB",
            scheduled_departure_at=now - timedelta(hours=5),
            scheduled_arrival_at=now - timedelta(hours=2),
            actual_arrival_at=now - timedelta(hours=2, minutes=5),
            gate_code="A15",
            stand_code="15",
            aircraft_registration="A6-EUC",
            leg_status="arrived",
            created_at=now,
            updated_at=now,
        ),
        JourneyLeg(
            id=str(uuid.UUID(int=204)),
            journey_id=journeys["journey2"].id,
            sequence_number=2,
            flight_number="EK103",
            departure_station="DXB",
            arrival_station="SIN",
            scheduled_departure_at=now + timedelta(hours=2, minutes=55),  # 85 min to cutoff
            scheduled_arrival_at=now + timedelta(hours=10),
            gate_code="C10",
            stand_code="50",
            aircraft_registration="A6-EUD",
            leg_status="scheduled",
            created_at=now,
            updated_at=now,
        ),
    ]
    
    for leg in legs:
        existing = db.query(JourneyLeg).filter(JourneyLeg.id == leg.id).first()
        if not existing:
            db.add(leg)
    
    db.commit()


def seed_bags(db: Session, journeys: dict) -> dict[str, Bag]:
    """Seed bags."""
    bag1 = Bag(
        id=str(uuid.UUID(int=301)),
        bag_tag="EK001234567",
        journey_id=journeys["journey1"].id,
        current_status_code="in_transfer",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    bag2 = Bag(
        id=str(uuid.UUID(int=302)),
        bag_tag="EK001234568",
        journey_id=journeys["journey1"].id,
        current_status_code="at_risk",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    bag3 = Bag(
        id=str(uuid.UUID(int=303)),
        bag_tag="EK001234569",
        journey_id=journeys["journey2"].id,
        current_status_code="on_time",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    # Passenger-friendly bag tag for passenger scenario (at-risk with estimated status)
    bag4 = Bag(
        id=str(uuid.UUID(int=304)),
        bag_tag="0176482193",
        journey_id=journeys["journey1"].id,
        current_status_code="at_risk",
        current_case_id=None,  # Will be linked to case1 in seed_case_bags
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    # On-time bag with confirmed status for passenger scenario
    bag5 = Bag(
        id=str(uuid.UUID(int=305)),
        bag_tag="0176482194",
        journey_id=journeys["journey2"].id,
        current_status_code="on_time",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    bags = {"bag1": bag1, "bag2": bag2, "bag3": bag3, "bag4": bag4, "bag5": bag5}
    
    for bag_key, bag in bags.items():
        existing = db.query(Bag).filter(Bag.id == bag.id).first()
        if not existing:
            db.add(bag)
    
    db.commit()
    return bags


def seed_bag_events(db: Session, bags: dict) -> None:
    """Seed bag events with realistic scenarios and varying freshness ages."""
    now = datetime.now(timezone.utc)
    
    events = [
        # Bag 1 (critical risk, 36 min to cutoff, fresh 2 min old)
        BagEvent(
            id=str(uuid.UUID(int=401)),
            bag_id=bags["bag1"].id,
            source_event_key="WASLA-EK001234567-001",
            source_system="Wasla",
            event_type="acceptance",
            event_station="JFK",
            observed_at=now - timedelta(hours=14),
            ingested_at=now - timedelta(hours=14),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_accepted", "location": "JFK", "agent": "JFK-AGT-001"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=402)),
            bag_id=bags["bag1"].id,
            source_event_key="BHS-EK001234567-002",
            source_system="BHS",
            event_type="loaded",
            event_station="JFK",
            observed_at=now - timedelta(hours=13),
            ingested_at=now - timedelta(hours=13),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_loaded", "flight": "EK0201", "uld": "AKE12345"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=403)),
            bag_id=bags["bag1"].id,
            source_event_key="BRS-EK001234567-003",
            source_system="BRS",
            event_type="arrived",
            event_station="DXB",
            observed_at=now - timedelta(hours=1, minutes=15),
            ingested_at=now - timedelta(hours=1, minutes=10),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_arrived", "location": "DXB", "belt": "11", "flight": "EK0201"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=404)),
            bag_id=bags["bag1"].id,
            source_event_key="DERIVED-EK001234567-004",
            source_system="flight_ops",
            event_type="transfer_pending",
            event_station="DXB",
            observed_at=now - timedelta(minutes=45),
            ingested_at=now - timedelta(minutes=2),  # Fresh: 2 minutes ago
            fact_type="derived",
            freshness_state="fresh",
            confidence_score=Decimal("0.75"),
            payload_json=json.dumps({"event": "transfer_pending", "target_flight": "EK101", "gate": "B05", "status": "awaiting_scan"}),
        ),
        
        # Bag 2 (high risk, 52 min to cutoff, stale 14+ min old)
        BagEvent(
            id=str(uuid.UUID(int=411)),
            bag_id=bags["bag2"].id,
            source_event_key="WASLA-EK001234568-001",
            source_system="Wasla",
            event_type="acceptance",
            event_station="JFK",
            observed_at=now - timedelta(hours=14, minutes=10),
            ingested_at=now - timedelta(hours=14, minutes=10),
            fact_type="observed",
            freshness_state="stale",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_accepted", "location": "JFK", "agent": "JFK-AGT-002"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=412)),
            bag_id=bags["bag2"].id,
            source_event_key="BHS-EK001234568-002",
            source_system="BHS",
            event_type="loaded",
            event_station="JFK",
            observed_at=now - timedelta(hours=13, minutes=5),
            ingested_at=now - timedelta(hours=13, minutes=5),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_loaded", "flight": "EK0201", "uld": "AKE12346"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=413)),
            bag_id=bags["bag2"].id,
            source_event_key="BRS-EK001234568-003",
            source_system="BRS",
            event_type="arrived",
            event_station="DXB",
            observed_at=now - timedelta(hours=1, minutes=20),
            ingested_at=now - timedelta(hours=1, minutes=15),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_arrived", "location": "DXB", "belt": "11", "flight": "EK0201"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=414)),
            bag_id=bags["bag2"].id,
            source_event_key="DERIVED-EK001234568-004",
            source_system="flight_ops",
            event_type="transfer_pending",
            event_station="DXB",
            observed_at=now - timedelta(hours=1),
            ingested_at=now - timedelta(minutes=14),  # Stale: 14 minutes ago
            fact_type="derived",
            freshness_state="stale",
            confidence_score=Decimal("0.70"),
            payload_json=json.dumps({"event": "transfer_pending", "target_flight": "EK101", "gate": "B05", "status": "awaiting_scan"}),
        ),
        
        # Bag 3 (medium risk, 1h25min to cutoff, fresh 6 min old)
        BagEvent(
            id=str(uuid.UUID(int=421)),
            bag_id=bags["bag3"].id,
            source_event_key="WASLA-EK001234569-001",
            source_system="Wasla",
            event_type="acceptance",
            event_station="LHR",
            observed_at=now - timedelta(hours=8),
            ingested_at=now - timedelta(hours=8),
            fact_type="observed",
            freshness_state="stale",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_accepted", "location": "LHR", "agent": "LHR-AGT-003"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=422)),
            bag_id=bags["bag3"].id,
            source_event_key="BHS-EK001234569-002",
            source_system="BHS",
            event_type="loaded",
            event_station="LHR",
            observed_at=now - timedelta(hours=7),
            ingested_at=now - timedelta(hours=7),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_loaded", "flight": "EK002", "uld": "AKE12347"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=423)),
            bag_id=bags["bag3"].id,
            source_event_key="BRS-EK001234569-003",
            source_system="BRS",
            event_type="arrived",
            event_station="DXB",
            observed_at=now - timedelta(hours=2),
            ingested_at=now - timedelta(hours=2),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_arrived", "location": "DXB", "belt": "12", "flight": "EK002"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=424)),
            bag_id=bags["bag3"].id,
            source_event_key="WASLA-EK001234569-004",
            source_system="Wasla",
            event_type="transfer_confirmed",
            event_station="DXB",
            observed_at=now - timedelta(minutes=30),
            ingested_at=now - timedelta(minutes=6),  # Fresh: 6 minutes ago
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "transfer_confirmed", "target_flight": "EK103", "gate": "C10", "handler": "DNATA"}),
        ),
        
        # Bag 4 (0176482193) - at-risk passenger scenario with estimated status
        BagEvent(
            id=str(uuid.UUID(int=431)),
            bag_id=bags["bag4"].id,
            source_event_key="WASLA-0176482193-001",
            source_system="Wasla",
            event_type="acceptance",
            event_station="LHR",
            observed_at=now - timedelta(hours=6),
            ingested_at=now - timedelta(hours=6),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_accepted", "location": "LHR", "agent": "LHR-AGT-004"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=432)),
            bag_id=bags["bag4"].id,
            source_event_key="BHS-0176482193-002",
            source_system="BHS",
            event_type="arrived",
            event_station="DXB",
            observed_at=now - timedelta(hours=1, minutes=2),
            ingested_at=now - timedelta(hours=1),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_arrived", "location": "DXB", "belt": "11"}),
        ),
        
        # Bag 5 (0176482194) - on-time passenger scenario with confirmed status
        BagEvent(
            id=str(uuid.UUID(int=441)),
            bag_id=bags["bag5"].id,
            source_event_key="WASLA-0176482194-001",
            source_system="Wasla",
            event_type="acceptance",
            event_station="LHR",
            observed_at=now - timedelta(hours=5),
            ingested_at=now - timedelta(hours=5),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_accepted", "location": "LHR", "agent": "LHR-AGT-005"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=442)),
            bag_id=bags["bag5"].id,
            source_event_key="BHS-0176482194-002",
            source_system="BHS",
            event_type="arrived",
            event_station="DXB",
            observed_at=now - timedelta(hours=2, minutes=5),
            ingested_at=now - timedelta(hours=2, minutes=5),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "bag_arrived", "location": "DXB", "belt": "12"}),
        ),
        BagEvent(
            id=str(uuid.UUID(int=443)),
            bag_id=bags["bag5"].id,
            source_event_key="WASLA-0176482194-003",
            source_system="Wasla",
            event_type="transfer_scan",
            event_station="DXB",
            observed_at=now - timedelta(minutes=45),
            ingested_at=now - timedelta(minutes=45),
            fact_type="observed",
            freshness_state="fresh",
            confidence_score=Decimal("1.00"),
            payload_json=json.dumps({"event": "transfer_scan", "target_flight": "EK103", "gate": "C10"}),
        ),
    ]
    
    for event in events:
        existing = db.query(BagEvent).filter(BagEvent.id == event.id).first()
        if not existing:
            db.add(event)
    
    db.commit()


def seed_exception_cases(db: Session, users: dict) -> dict[str, ExceptionCase]:
    """Seed exception cases with varying risk levels and freshness states matching task requirements."""
    now = datetime.now(timezone.utc)
    
    # Case 1: Critical risk, 3 bags, BC-DXB-240611
    case1 = ExceptionCase(
        id=str(uuid.UUID(int=501)),
        case_reference="BC-DXB-240611",
        exception_type="short_connection_risk",
        severity_code="critical",
        deadline_at=now + timedelta(hours=2, minutes=6),
        status_code="open",
        observed_state_summary="3 bags arrived DXB, transfer scans missing, 36 minutes to cutoff",
        predicted_state_summary="Critical: approaching cutoff, requires immediate expedited handling",
        created_by_user_id=users["operations"].id,
        created_at=now - timedelta(hours=1),
        updated_at=now - timedelta(hours=1),
    )
    
    # Case 2: High risk, 2 bags, BC-DXB-240612
    case2 = ExceptionCase(
        id=str(uuid.UUID(int=502)),
        case_reference="BC-DXB-240612",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=now + timedelta(hours=2, minutes=22),
        status_code="open",
        observed_state_summary="2 bags arrived DXB, transfer scan stale (14 min old), 52 minutes to cutoff",
        predicted_state_summary="Connection at risk, late inbound detected",
        created_by_user_id=users["operations"].id,
        created_at=now - timedelta(minutes=50),
        updated_at=now - timedelta(minutes=50),
    )
    
    # Case 3: High risk, 2 bags, BC-DXB-240613
    case3 = ExceptionCase(
        id=str(uuid.UUID(int=503)),
        case_reference="BC-DXB-240613",
        exception_type="transfer_monitoring",
        severity_code="high",
        deadline_at=now + timedelta(hours=2, minutes=55),
        status_code="open",
        observed_state_summary="2 bags transfer confirmed, monitoring tight connection window",
        predicted_state_summary="High: adequate buffer but requires monitoring",
        created_by_user_id=users["operations"].id,
        created_at=now - timedelta(minutes=35),
        updated_at=now - timedelta(minutes=35),
    )
    
    # Case 4: Medium risk, 1 bag, BC-DXB-240614
    case4 = ExceptionCase(
        id=str(uuid.UUID(int=504)),
        case_reference="BC-DXB-240614",
        exception_type="transfer_monitoring",
        severity_code="medium",
        deadline_at=now + timedelta(hours=3, minutes=30),
        status_code="open",
        observed_state_summary="1 bag transfer confirmed, sufficient connection window",
        predicted_state_summary="Moderate: sufficient buffer, continue monitoring",
        created_by_user_id=users["operations"].id,
        created_at=now - timedelta(minutes=20),
        updated_at=now - timedelta(minutes=20),
    )
    
    cases = {"case1": case1, "case2": case2, "case3": case3, "case4": case4}
    
    for case_key, case in cases.items():
        existing = db.query(ExceptionCase).filter(ExceptionCase.id == case.id).first()
        if not existing:
            db.add(case)
    
    db.commit()
    return cases


def seed_case_bags(db: Session, cases: dict, bags: dict) -> None:
    """Seed case-bag memberships - case1 with 4 bags (including passenger-friendly bag), case2 with 2, case3 with 2, case4 with 1."""
    case_bags = [
        # Case 1: 4 bags (critical, includes passenger-friendly bag 0176482193)
        CaseBag(
            case_id=cases["case1"].id,
            bag_id=bags["bag1"].id,
            primary_flag=True,
            created_at=datetime.now(timezone.utc),
        ),
        CaseBag(
            case_id=cases["case1"].id,
            bag_id=bags["bag2"].id,
            primary_flag=False,
            created_at=datetime.now(timezone.utc),
        ),
        CaseBag(
            case_id=cases["case1"].id,
            bag_id=bags["bag3"].id,
            primary_flag=False,
            created_at=datetime.now(timezone.utc),
        ),
        CaseBag(
            case_id=cases["case1"].id,
            bag_id=bags["bag4"].id,
            primary_flag=False,
            created_at=datetime.now(timezone.utc),
        ),
        # Case 2: 2 bags (high)
        CaseBag(
            case_id=cases["case2"].id,
            bag_id=bags["bag1"].id,
            primary_flag=True,
            created_at=datetime.now(timezone.utc),
        ),
        CaseBag(
            case_id=cases["case2"].id,
            bag_id=bags["bag2"].id,
            primary_flag=False,
            created_at=datetime.now(timezone.utc),
        ),
        # Case 3: 2 bags (high)
        CaseBag(
            case_id=cases["case3"].id,
            bag_id=bags["bag2"].id,
            primary_flag=True,
            created_at=datetime.now(timezone.utc),
        ),
        CaseBag(
            case_id=cases["case3"].id,
            bag_id=bags["bag3"].id,
            primary_flag=False,
            created_at=datetime.now(timezone.utc),
        ),
        # Case 4: 1 bag (medium)
        CaseBag(
            case_id=cases["case4"].id,
            bag_id=bags["bag3"].id,
            primary_flag=True,
            created_at=datetime.now(timezone.utc),
        ),
    ]
    
    for case_bag in case_bags:
        existing = db.query(CaseBag).filter(
            CaseBag.case_id == case_bag.case_id,
            CaseBag.bag_id == case_bag.bag_id
        ).first()
        if not existing:
            db.add(case_bag)
    
    db.commit()
    
    # Update bag.current_case_id for all bags in cases
    # This allows PassengerStatusService to find the case view when composing bag status
    for case_key, case in cases.items():
        # Get all bags for this case
        case_bags_for_case = db.query(CaseBag).filter(CaseBag.case_id == case.id).all()
        
        for case_bag in case_bags_for_case:
            bag = db.query(Bag).filter(Bag.id == case_bag.bag_id).first()
            if bag:
                # Set current_case_id to the most recent case (last one wins if bag is in multiple cases)
                bag.current_case_id = case.id
    
    db.commit()


def seed_recommendations(db: Session, cases: dict) -> dict[str, Recommendation]:
    """Seed recommendations with top recommendation (0.85), alternative (0.72), and superseded older one."""
    now = datetime.now(timezone.utc)
    
    # Top recommendation for case1 - confidence 0.85
    rec1 = Recommendation(
        id=str(uuid.UUID(int=601)),
        case_id=cases["case1"].id,
        action_code="PRIORITY_TRANSFER",
        action_label="Expedite Transfer to Gate B05",
        reason_text="Bags require expedited handling to meet EK101 connection window. With 36 minutes to cutoff and critical severity, priority transfer minimizes misconnection risk.",
        confidence_score=Decimal("0.85"),
        freshness_state="fresh",
        evidence_json=json.dumps({
            "bag_tags": ["EK001234567", "EK001234568", "EK001234569"],
            "time_to_deadline_minutes": 36,
            "severity": "critical",
            "current_bag_location": "arrival_belt_11",
            "target_gate": "B05",
            "target_flight": "EK101"
        }),
        generated_at=now - timedelta(minutes=30),
    )
    
    # Alternative recommendation for case1 - confidence 0.72
    rec2 = Recommendation(
        id=str(uuid.UUID(int=602)),
        case_id=cases["case1"].id,
        action_code="MONITOR",
        action_label="Continue Monitoring Connection",
        reason_text="Current connection window provides minimal buffer. Continue monitoring for transfer scan confirmation. Escalate if no scan within 15 minutes.",
        confidence_score=Decimal("0.72"),
        freshness_state="fresh",
        evidence_json=json.dumps({
            "bag_tags": ["EK001234567", "EK001234568", "EK001234569"],
            "time_to_deadline_minutes": 36,
            "severity": "critical",
            "current_status": "in_transfer"
        }),
        generated_at=now - timedelta(minutes=30),
    )
    
    # Superseded older recommendation for case1
    rec3 = Recommendation(
        id=str(uuid.UUID(int=603)),
        case_id=cases["case1"].id,
        action_code="LOCATE_BAG",
        action_label="Initiate Bag Search",
        reason_text="Bags not scanned at transfer point, initiate search procedure.",
        confidence_score=Decimal("0.78"),
        freshness_state="stale",
        evidence_json=json.dumps({
            "bag_tags": ["EK001234567", "EK001234568", "EK001234569"],
            "last_known_location": "arrival_belt_11"
        }),
        generated_at=now - timedelta(hours=1, minutes=15),
        superseded_at=now - timedelta(minutes=30),  # Superseded when new recs generated
    )
    
    # Recommendation for case2
    rec4 = Recommendation(
        id=str(uuid.UUID(int=604)),
        case_id=cases["case2"].id,
        action_code="PRIORITY_TRANSFER",
        action_label="Expedite Transfer to Gate C10",
        reason_text="Bags require expedited handling. With 52 minutes to cutoff and high severity, priority transfer recommended.",
        confidence_score=Decimal("0.80"),
        freshness_state="stale",
        evidence_json=json.dumps({
            "bag_tags": ["EK001234569"],
            "time_to_deadline_minutes": 52,
            "severity": "high"
        }),
        generated_at=now - timedelta(minutes=20),
    )
    
    # Recommendation for case3 (medium severity, locate bag)
    rec5 = Recommendation(
        id=str(uuid.UUID(int=605)),
        case_id=cases["case3"].id,
        action_code="LOCATE_BAG",
        action_label="Initiate Bag Search",
        reason_text="Bag missing from expected transfer location. Initiate search procedure to locate and expedite to gate.",
        confidence_score=Decimal("0.75"),
        freshness_state="fresh",
        evidence_json=json.dumps({
            "bag_tags": ["EK001234570"],
            "time_to_deadline_minutes": 85,
            "severity": "medium"
        }),
        generated_at=now - timedelta(minutes=35),
    )
    
    recs = {"rec1": rec1, "rec2": rec2, "rec3": rec3, "rec4": rec4, "rec5": rec5}
    
    for rec_key, rec in recs.items():
        existing = db.query(Recommendation).filter(Recommendation.id == rec.id).first()
        if not existing:
            db.add(rec)
    
    db.commit()
    return recs


def seed_approval_decisions(db: Session, cases: dict, recs: dict, users: dict) -> None:
    """
    Seed approval decisions.
    Some approved with tasks generated, some rejected with rationale, some cases pending approval with no decision yet.
    """
    now = datetime.now(timezone.utc)
    
    approvals = [
        # Case1 rec1 - Approved, tasks will be generated
        ApprovalDecision(
            id=str(uuid.UUID(int=701)),
            case_id=cases["case1"].id,
            recommendation_id=recs["rec1"].id,
            decided_by_user_id=users["operations"].id,
            decision_code="approved",
            rationale_text="Connection window critical, expedite approved",
            decided_at=now - timedelta(minutes=25),
            decision_version=1,
        ),
        # Case2 rec4 - Approved, tasks will be generated
        ApprovalDecision(
            id=str(uuid.UUID(int=702)),
            case_id=cases["case2"].id,
            recommendation_id=recs["rec4"].id,
            decided_by_user_id=users["operations"].id,
            decision_code="approved",
            rationale_text="Risk justified, approve priority transfer",
            decided_at=now - timedelta(minutes=18),
            decision_version=1,
        ),
        # Case1 rec2 - Rejected (alternative was not chosen)
        ApprovalDecision(
            id=str(uuid.UUID(int=703)),
            case_id=cases["case1"].id,
            recommendation_id=recs["rec2"].id,
            decided_by_user_id=users["operations"].id,
            decision_code="rejected",
            rationale_text="Passive monitoring insufficient given critical severity. Active intervention required.",
            decided_at=now - timedelta(minutes=25),
            decision_version=1,
        ),
        # Case3 rec5 - Approved, task generated
        ApprovalDecision(
            id=str(uuid.UUID(int=704)),
            case_id=cases["case3"].id,
            recommendation_id=recs["rec5"].id,
            decided_by_user_id=users["operations"].id,
            decision_code="approved",
            rationale_text="Bag search approved, sufficient buffer time remains",
            decided_at=now - timedelta(minutes=32),
            decision_version=1,
        ),
    ]
    
    for approval in approvals:
        existing = db.query(ApprovalDecision).filter(ApprovalDecision.id == approval.id).first()
        if not existing:
            db.add(approval)
    
    db.commit()


def seed_tasks(db: Session, cases: dict, recs: dict) -> dict[str, Task]:
    """
    Seed tasks generated from approved recommendations.
    
    Task IDs: TSK-DXB-1187, TSK-DXB-1189 (assigned to partner),
              TSK-DXB-1181 (acknowledged), TSK-DXB-1176 (in_progress)
    """
    now = datetime.now(timezone.utc)
    
    tasks = {
        # TSK-DXB-1187 - Case1 rec1, assigned to partner, status assigned
        "task1": Task(
            id=str(uuid.UUID(int=1187)),
            case_id=cases["case1"].id,
            recommendation_id=recs["rec1"].id,
            assigned_role_code="partner",
            assigned_partner_org_code="DNATA",
            bag_reference="EK001234567",
            station_code="DXB",
            flight_context_text="EK101 DXB-SYD, departure in 2h6min, gate B05",
            instruction_text="Expedite bag EK001234567 from arrival belt 11 to gate B05 for EK101. Critical connection window.",
            evidence_links_json=json.dumps(["Bag event log", "Transfer scan history", "Flight departure schedule"]),
            deadline_at=now + timedelta(hours=1, minutes=36),
            status_code="assigned",
            created_at=now - timedelta(minutes=25),
            updated_at=now - timedelta(minutes=25),
        ),
        # TSK-DXB-1189 - Case1 rec1, assigned to partner (second bag), status assigned
        "task2": Task(
            id=str(uuid.UUID(int=1189)),
            case_id=cases["case1"].id,
            recommendation_id=recs["rec1"].id,
            assigned_role_code="partner",
            assigned_partner_org_code="DNATA",
            bag_reference="EK001234568",
            station_code="DXB",
            flight_context_text="EK101 DXB-SYD, departure in 2h6min, gate B05",
            instruction_text="Expedite bag EK001234568 from arrival belt 11 to gate B05 for EK101. Critical connection window.",
            evidence_links_json=json.dumps(["Bag event log", "Transfer scan history", "Flight departure schedule"]),
            deadline_at=now + timedelta(hours=1, minutes=36),
            status_code="assigned",
            created_at=now - timedelta(minutes=25),
            updated_at=now - timedelta(minutes=25),
        ),
        # TSK-DXB-1181 - Case2 rec4, assigned to partner, status acknowledged
        "task3": Task(
            id=str(uuid.UUID(int=1181)),
            case_id=cases["case2"].id,
            recommendation_id=recs["rec4"].id,
            assigned_role_code="partner",
            assigned_partner_org_code="DNATA",
            bag_reference="EK001234569",
            station_code="DXB",
            flight_context_text="EK103 DXB-SIN, departure in 2h55min, gate C10",
            instruction_text="Expedite bag EK001234569 to gate C10 for EK103.",
            evidence_links_json=json.dumps(["Bag event log", "Transfer scan history", "Flight departure schedule"]),
            deadline_at=now + timedelta(hours=2, minutes=25),
            status_code="acknowledged",
            created_at=now - timedelta(minutes=18),
            updated_at=now - timedelta(minutes=10),
        ),
        # TSK-DXB-1176 - Case3, assigned to partner, status in_progress
        "task4": Task(
            id=str(uuid.UUID(int=1176)),
            case_id=cases["case3"].id,
            recommendation_id=str(uuid.UUID(int=605)),  # Placeholder rec ID for case3
            assigned_role_code="partner",
            assigned_partner_org_code="DNATA",
            bag_reference="EK001234570",
            station_code="DXB",
            flight_context_text="EK105 DXB-BKK, departure in 3h15min, gate D08",
            instruction_text="Locate bag EK001234570 in transfer area. Confirm current location and status.",
            evidence_links_json=json.dumps(["Last known location", "Transfer scan history", "Station baggage hold map"]),
            deadline_at=now + timedelta(hours=2, minutes=45),
            status_code="in_progress",
            created_at=now - timedelta(minutes=30),
            updated_at=now - timedelta(minutes=5),
        ),
    }
    
    for task_key, task in tasks.items():
        existing = db.query(Task).filter(Task.id == task.id).first()
        if not existing:
            db.add(task)
    
    db.commit()
    return tasks


def seed_task_evidence(db: Session, tasks: dict, users: dict) -> None:
    """
    Seed task evidence for acknowledged and in_progress tasks.
    
    Implements FR-010: task acknowledgement and evidence capture.
    Includes acknowledgement, scan confirmation, handover proof, completion note, and blocker reason.
    """
    now = datetime.now(timezone.utc)
    
    evidences = [
        # Evidence for task3 (TSK-DXB-1181) - acknowledged with scan confirmation
        TaskEvidence(
            id=str(uuid.UUID(int=901)),
            task_id=tasks["task3"].id,
            actor_user_id=users["partner"].id,
            event_type="acknowledged",
            note_text="Task acknowledged, bag located at belt 11, proceeding to gate C10",
            evidence_type="scan_confirmation",
            evidence_reference="SCAN-DXB-001234569-001",
            client_event_id="CLIENT-EVT-001",
            recorded_at=now - timedelta(minutes=10),
        ),
        # Evidence for task4 (TSK-DXB-1176) - acknowledged, then in_progress with scan confirmation
        TaskEvidence(
            id=str(uuid.UUID(int=902)),
            task_id=tasks["task4"].id,
            actor_user_id=users["partner"].id,
            event_type="acknowledged",
            note_text="Task acknowledged, initiating bag search in transfer area",
            client_event_id="CLIENT-EVT-002",
            recorded_at=now - timedelta(minutes=28),
        ),
        TaskEvidence(
            id=str(uuid.UUID(int=903)),
            task_id=tasks["task4"].id,
            actor_user_id=users["partner"].id,
            event_type="in_progress",
            note_text="Bag located in holding area zone 3, preparing for transfer to gate D08",
            evidence_type="scan_confirmation",
            evidence_reference="SCAN-DXB-001234570-002",
            client_event_id="CLIENT-EVT-003",
            recorded_at=now - timedelta(minutes=5),
        ),
        # Additional evidence showing completion with handover proof
        TaskEvidence(
            id=str(uuid.UUID(int=904)),
            task_id=tasks["task3"].id,
            actor_user_id=users["partner"].id,
            event_type="evidence_submitted",
            note_text="Bag successfully delivered to gate C10, handover confirmed",
            evidence_type="handover_proof",
            evidence_reference="HANDOVER-DXB-001234569-C10",
            client_event_id="CLIENT-EVT-004",
            recorded_at=now - timedelta(minutes=5),
        ),
    ]
    
    for evidence in evidences:
        existing = db.query(TaskEvidence).filter(TaskEvidence.id == evidence.id).first()
        if not existing:
            db.add(evidence)
    
    db.commit()


def seed_passenger_case_views(db: Session, cases: dict) -> None:
    """
    Seed passenger case views with confirmed and estimated status.
    
    Implements FR-012, FR-013, FR-014: passenger-safe case status with separation of
    confirmed vs estimated information and progress steps.
    
    Two test scenarios:
    1. BC-DXB-240611: Delayed-bag case with estimated status ("Being prioritised")
    2. Closed case with confirmed delivery status ("Delivered to belt 5")
    """
    now = datetime.now(timezone.utc)
    
    views = [
        # Case1 (BC-DXB-240611) - delayed-bag case with estimated status
        PassengerCaseView(
            id=str(uuid.UUID(int=1001)),
            case_id=cases["case1"].id,
            case_reference=cases["case1"].case_reference,  # BC-DXB-240611
            latest_confirmed_status="Arrived at Dubai 19:58 GST",
            estimated_notice="Being prioritised for onward flight. Estimated notice: delivery to gate within 60 minutes",
            next_expected_update="2 hours before departure",
            passenger_safe_payload_json=json.dumps({
                "progress_steps": [
                    {
                        "step_text": "Arrived at Dubai 19:58 GST",
                        "status": "confirmed",
                        "timestamp": (now - timedelta(hours=1, minutes=2)).isoformat()
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
            refreshed_at=now,
        ),
        # Closed case with confirmed delivery
        PassengerCaseView(
            id=str(uuid.UUID(int=1002)),
            case_id=cases["case2"].id,
            case_reference=cases["case2"].case_reference,  # BC-DXB-240612
            latest_confirmed_status="Delivered to belt 5",
            estimated_notice=None,
            next_expected_update="Case resolved",
            passenger_safe_payload_json=json.dumps({
                "progress_steps": [
                    {
                        "step_text": "Arrived at Dubai 19:03 GST",
                        "status": "confirmed",
                        "timestamp": (now - timedelta(hours=2)).isoformat()
                    },
                    {
                        "step_text": "Scanned at transfer area 19:17 GST",
                        "status": "confirmed",
                        "timestamp": (now - timedelta(hours=1, minutes=46)).isoformat()
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
            refreshed_at=now,
        ),
    ]
    
    for view in views:
        existing = db.query(PassengerCaseView).filter(PassengerCaseView.id == view.id).first()
        if not existing:
            db.add(view)
    
    db.commit()


def seed_executive_metrics(db: Session) -> None:
    """
    Seed executive daily metrics for the last 14 days (2026-11-10 to 2026-11-23).
    Implements FR-017: executive reliability and impact overview with known KPI values.
    
    Known aggregate KPIs from requirements:
    - Exception rate: 1.8 per 1000 bags
    - Recovered before departure: 75%
    - Mean decision time: 11 minutes
    - Passengers impacted: 168 total over period
    - Open ageing: 3.2 hours average
    - Stale data: 2 of 3 sources
    """
    today = datetime.now(timezone.utc).date()
    
    # Generate 14 days of metrics ending today (2026-11-10 to 2026-11-23)
    metrics = []
    for day_offset in range(13, -1, -1):  # 14 days: 13 days ago to today
        metric_date = today - timedelta(days=day_offset)
        
        # Vary metrics slightly per day to show trends
        # Base values to achieve aggregate KPIs
        base_open_cases = 3 + (day_offset % 3)  # Vary 3-5 per day
        base_urgent = 1 + (day_offset % 2)      # Vary 1-2 per day
        base_recovered = int(base_open_cases * 0.75)  # 75% recovery rate
        base_passengers = 10 + (day_offset % 5)  # Vary 10-14 per day
        base_stale = 2 if day_offset % 7 < 3 else 1  # 2 of 3 sources on some days
        
        metric_id_base = 1101 + (13 - day_offset)
        
        metric = ExecutiveDailyMetric(
            id=str(uuid.UUID(int=metric_id_base)),
            metric_date=metric_date,
            station_code="DXB",
            open_case_count=base_open_cases,
            urgent_case_count=base_urgent,
            recovered_before_departure_count=base_recovered,
            impacted_passenger_count=base_passengers,
            stale_data_case_count=base_stale,
            snapshot_generated_at=datetime.combine(metric_date, datetime.min.time()) + timedelta(hours=23, minutes=59),
        )
        
        metrics.append(metric)
    
    for metric in metrics:
        existing = db.query(ExecutiveDailyMetric).filter(
            ExecutiveDailyMetric.metric_date == metric.metric_date,
            ExecutiveDailyMetric.station_code == metric.station_code
        ).first()
        if not existing:
            db.add(metric)
    
    db.commit()


def seed_audit_events(db: Session, users: dict, cases: dict) -> None:
    """
    Seed comprehensive audit events covering login, approval decisions, task evidence, and case actions.
    Implements FR-016: audit trail with actor, action, timestamp, entity context, correlation ID, and outcome.
    """
    now = datetime.now(timezone.utc)
    base_correlation_id = str(uuid.uuid4())
    
    events = [
        # Login events (success and failure)
        AuditEvent(
            id=str(uuid.UUID(int=1201)),
            actor_user_id=users["operations"].id,
            action_type="login_success",
            entity_type="user",
            entity_id=users["operations"].id,
            correlation_id=str(uuid.uuid4()),
            outcome_code="success",
            detail_json=json.dumps({"email": "mariam.alsuwaidi@baggage360.demo", "role": "operations"}),
            occurred_at=now - timedelta(hours=2),
        ),
        AuditEvent(
            id=str(uuid.UUID(int=1202)),
            actor_user_id=None,  # System action for failed login
            action_type="login_failure",
            entity_type="user",
            entity_id="unknown",
            correlation_id=str(uuid.uuid4()),
            outcome_code="failure",
            detail_json=json.dumps({"email": "invalid@example.com", "reason": "invalid_credentials"}),
            occurred_at=now - timedelta(hours=3),
        ),
        AuditEvent(
            id=str(uuid.UUID(int=1203)),
            actor_user_id=users["partner"].id,
            action_type="login_success",
            entity_type="user",
            entity_id=users["partner"].id,
            correlation_id=str(uuid.uuid4()),
            outcome_code="success",
            detail_json=json.dumps({"email": "ahmed.hassan@dnata.ae", "role": "partner", "partner_org": "DNATA"}),
            occurred_at=now - timedelta(hours=1, minutes=30),
        ),
        
        # Case creation
        AuditEvent(
            id=str(uuid.UUID(int=1204)),
            actor_user_id=users["operations"].id,
            action_type="case_created",
            entity_type="exception_case",
            entity_id=cases["case1"].id,
            correlation_id=base_correlation_id,
            outcome_code="success",
            detail_json=json.dumps({
                "case_reference": cases["case1"].case_reference,
                "severity": "critical",
                "bag_count": 3
            }),
            occurred_at=now - timedelta(hours=1),
        ),
        
        # Approval decisions with actor and outcome
        AuditEvent(
            id=str(uuid.UUID(int=1205)),
            actor_user_id=users["operations"].id,
            action_type="approval_decision_approved",
            entity_type="approval_decision",
            entity_id=str(uuid.UUID(int=701)),  # Case1 rec1 approval
            correlation_id=base_correlation_id,
            outcome_code="success",
            detail_json=json.dumps({
                "case_id": cases["case1"].id,
                "case_reference": cases["case1"].case_reference,
                "recommendation_id": str(uuid.UUID(int=601)),
                "action_code": "PRIORITY_TRANSFER",
                "rationale": "Connection window critical, expedite approved"
            }),
            occurred_at=now - timedelta(minutes=25),
        ),
        AuditEvent(
            id=str(uuid.UUID(int=1206)),
            actor_user_id=users["operations"].id,
            action_type="approval_decision_rejected",
            entity_type="approval_decision",
            entity_id=str(uuid.UUID(int=703)),  # Case1 rec2 rejection
            correlation_id=base_correlation_id,
            outcome_code="success",
            detail_json=json.dumps({
                "case_id": cases["case1"].id,
                "case_reference": cases["case1"].case_reference,
                "recommendation_id": str(uuid.UUID(int=602)),
                "action_code": "MONITOR",
                "rationale": "Passive monitoring insufficient given critical severity"
            }),
            occurred_at=now - timedelta(minutes=25),
        ),
        
        # Task evidence submission
        AuditEvent(
            id=str(uuid.UUID(int=1207)),
            actor_user_id=users["partner"].id,
            action_type="task_evidence_submitted",
            entity_type="task",
            entity_id=str(uuid.UUID(int=1181)),  # TSK-DXB-1181
            correlation_id=str(uuid.uuid4()),
            outcome_code="success",
            detail_json=json.dumps({
                "task_id": str(uuid.UUID(int=1181)),
                "event_type": "acknowledged",
                "evidence_type": "scan_confirmation",
                "evidence_reference": "SCAN-DXB-001234569-001"
            }),
            occurred_at=now - timedelta(minutes=10),
        ),
        AuditEvent(
            id=str(uuid.UUID(int=1208)),
            actor_user_id=users["partner"].id,
            action_type="task_evidence_submitted",
            entity_type="task",
            entity_id=str(uuid.UUID(int=1176)),  # TSK-DXB-1176
            correlation_id=str(uuid.uuid4()),
            outcome_code="success",
            detail_json=json.dumps({
                "task_id": str(uuid.UUID(int=1176)),
                "event_type": "in_progress",
                "evidence_type": "scan_confirmation",
                "evidence_reference": "SCAN-DXB-001234570-002"
            }),
            occurred_at=now - timedelta(minutes=5),
        ),
        
        # Case closure action
        AuditEvent(
            id=str(uuid.UUID(int=1209)),
            actor_user_id=users["operations"].id,
            action_type="case_closed",
            entity_type="exception_case",
            entity_id=cases["case2"].id,
            correlation_id=str(uuid.uuid4()),
            outcome_code="success",
            detail_json=json.dumps({
                "case_reference": cases["case2"].case_reference,
                "resolution": "bags_recovered",
                "tasks_completed": 1
            }),
            occurred_at=now - timedelta(minutes=15),
        ),
    ]
    
    for event in events:
        existing = db.query(AuditEvent).filter(AuditEvent.id == event.id).first()
        if not existing:
            db.add(event)
    
    db.commit()


def seed_session_access_log(db: Session, users: dict, cases: dict) -> None:
    """Seed session access log."""
    log = SessionAccessLog(
        id=str(uuid.UUID(int=1301)),
        actor_user_id=users["operations"].id,
        access_purpose="case_review",
        resource_type="exception_case",
        resource_id=cases["case1"].id,
        decision_code="allow",
        correlation_id=str(uuid.uuid4()),
        occurred_at=datetime.now(timezone.utc) - timedelta(minutes=45),
    )
    
    existing = db.query(SessionAccessLog).filter(SessionAccessLog.id == log.id).first()
    if not existing:
        db.add(log)
    
    db.commit()


def run_seed():
    """Run all seed operations."""
    print("Starting seed data generation...")
    
    db = SessionLocal()
    try:
        users = seed_users(db)
        print("✓ Users seeded")
        
        journeys = seed_journeys(db, users)
        print("✓ Journeys seeded")
        
        seed_journey_legs(db, journeys)
        print("✓ Journey legs seeded")
        
        bags = seed_bags(db, journeys)
        print("✓ Bags seeded")
        
        seed_bag_events(db, bags)
        print("✓ Bag events seeded")
        
        cases = seed_exception_cases(db, users)
        print("✓ Exception cases seeded")
        
        seed_case_bags(db, cases, bags)
        print("✓ Case-bag memberships seeded")
        
        recs = seed_recommendations(db, cases)
        print("✓ Recommendations seeded")
        
        seed_approval_decisions(db, cases, recs, users)
        print("✓ Approval decisions seeded")
        
        tasks = seed_tasks(db, cases, recs)
        print("✓ Tasks seeded")
        
        seed_task_evidence(db, tasks, users)
        print("✓ Task evidence seeded")
        
        seed_passenger_case_views(db, cases)
        print("✓ Passenger case views seeded")
        
        seed_executive_metrics(db)
        print("✓ Executive metrics seeded")
        
        seed_audit_events(db, users, cases)
        print("✓ Audit events seeded")
        
        seed_session_access_log(db, users, cases)
        print("✓ Session access log seeded")
        
        print("\nSeed data generation complete!")
        print("\nDemo credentials:")
        print("  Operations: mariam.alsuwaidi@baggage360.demo / Demo1234!")
        print("  Partner:    ahmed.hassan@dnata.ae / Demo1234!")
        print("  Passenger:  sara.johnson@example.com / Demo1234!")
        print("  Executive:  fatima.albanna@emirates.ae / Demo1234!")
        
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
