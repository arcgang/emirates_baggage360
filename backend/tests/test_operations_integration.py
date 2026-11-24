"""Integration tests for operations API endpoints."""
import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from app.models import (
    User, ExceptionCase, Recommendation, Bag, PassengerJourney,
    JourneyLeg, BagEvent, ApprovalDecision, Task, CaseBag
)


def test_post_case_approval_with_approve_decision(client, db_session):
    """Test POST /api/v1/operations/cases/{case_id}/approvals with approve decision."""
    # Setup: Create test data
    user = User(
        id="00000000-0000-0000-0000-000000000001",
        external_subject="ops@test.com",
        role_code="operations",
        display_name="Ops User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    journey = PassengerJourney(
        id="journey-001",
        passenger_reference="PAX-001",
        pnr_reference="PNR-001",
        itinerary_status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(journey)
    
    bag = Bag(
        id="bag-001",
        bag_tag="TEST001",
        journey_id="journey-001",
        current_status_code="in_transfer",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(bag)
    
    case = ExceptionCase(
        id="case-001",
        case_reference="BC-TEST-001",
        exception_type="short_connection_risk",
        severity_code="critical",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(case)
    
    # Link bag to case
    case_bag = CaseBag(
        case_id="case-001",
        bag_id="bag-001",
        primary_flag=True,
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(case_bag)
    
    recommendation = Recommendation(
        id="rec-001",
        case_id="case-001",
        action_code="PRIORITY_TRANSFER",
        action_label="Priority Transfer",
        reason_text="Test reason",
        confidence_score=Decimal("0.85"),
        freshness_state="fresh",
        evidence_json=json.dumps({"test": "evidence"}),
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(recommendation)
    db_session.commit()
    
    # Test: Submit approval
    response = client.post(
        "/api/v1/operations/cases/case-001/approvals",
        json={
            "recommendation_id": "rec-001",
            "decision": "approve",
            "rationale": "Test approval rationale"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "case-001"
    assert data["recommendation_id"] == "rec-001"
    assert data["decision"] == "approve"
    assert "decided_at" in data
    assert data["decided_by"] == "Ops User"
    assert len(data["tasks_created"]) > 0
    
    # Verify approval was recorded
    approval = db_session.query(ApprovalDecision).filter(
        ApprovalDecision.case_id == "case-001",
        ApprovalDecision.recommendation_id == "rec-001"
    ).first()
    assert approval is not None
    assert approval.decision_code == "approved"
    assert approval.rationale_text == "Test approval rationale"


def test_post_case_approval_with_reject_decision(client, db_session):
    """Test POST /api/v1/operations/cases/{case_id}/approvals with reject decision."""
    # Setup: Create test data
    user = User(
        id="00000000-0000-0000-0000-000000000001",
        external_subject="ops@test.com",
        role_code="operations",
        display_name="Ops User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    case = ExceptionCase(
        id="case-002",
        case_reference="BC-TEST-002",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(case)
    
    recommendation = Recommendation(
        id="rec-002",
        case_id="case-002",
        action_code="MONITOR",
        action_label="Monitor",
        reason_text="Test reason",
        confidence_score=Decimal("0.75"),
        freshness_state="fresh",
        evidence_json=json.dumps({"test": "evidence"}),
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(recommendation)
    db_session.commit()
    
    # Test: Submit rejection
    response = client.post(
        "/api/v1/operations/cases/case-002/approvals",
        json={
            "recommendation_id": "rec-002",
            "decision": "reject",
            "rationale": "Not appropriate for current situation"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "case-002"
    assert data["recommendation_id"] == "rec-002"
    assert data["decision"] == "reject"
    assert len(data["tasks_created"]) == 0
    
    # Verify no tasks were created
    tasks = db_session.query(Task).filter(Task.case_id == "case-002").all()
    assert len(tasks) == 0


def test_post_case_approval_with_nonexistent_case(client, db_session):
    """Test POST /api/v1/operations/cases/{case_id}/approvals with nonexistent case."""
    response = client.post(
        "/api/v1/operations/cases/nonexistent-case/approvals",
        json={
            "recommendation_id": "rec-001",
            "decision": "approve",
            "rationale": "Test"
        }
    )
    
    assert response.status_code == 404
    assert "detail" in response.json()


def test_post_case_approval_with_nonexistent_recommendation(client, db_session):
    """Test POST /api/v1/operations/cases/{case_id}/approvals with nonexistent recommendation."""
    # Setup: Create case only
    user = User(
        id="00000000-0000-0000-0000-000000000001",
        external_subject="ops@test.com",
        role_code="operations",
        display_name="Ops User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    case = ExceptionCase(
        id="case-003",
        case_reference="BC-TEST-003",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(case)
    db_session.commit()
    
    response = client.post(
        "/api/v1/operations/cases/case-003/approvals",
        json={
            "recommendation_id": "nonexistent-rec",
            "decision": "approve",
            "rationale": "Test"
        }
    )
    
    assert response.status_code == 404
    assert "detail" in response.json()
