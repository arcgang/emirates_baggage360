"""Tests for ApprovalService."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import User, ExceptionCase, Recommendation, ApprovalDecision
from app.services.approval_service import ApprovalService


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_data(db_session):
    """Create test users, cases, and recommendations."""
    # Create user
    user = User(
        id=str(uuid.uuid4()),
        external_subject="test.ops@example.com",
        role_code="operations",
        display_name="Test Ops User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    # Create exception case
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="TEST-CASE-001",
        exception_type="transfer_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Bags in transfer",
        predicted_state_summary="At risk of misconnection",
        created_by_user_id=user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(case)
    
    # Create recommendation
    recommendation = Recommendation(
        id=str(uuid.uuid4()),
        case_id=case.id,
        action_code="PRIORITY_TRANSFER",
        action_label="Expedite Transfer",
        reason_text="Time critical",
        confidence_score=0.85,
        freshness_state="fresh",
        evidence_json='{"time_to_cutoff": 90}',
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(recommendation)
    
    db_session.commit()
    
    return {
        "user": user,
        "case": case,
        "recommendation": recommendation
    }


def test_record_approval_approved(db_session, test_data):
    """Test recording an approved decision."""
    service = ApprovalService(db_session)
    
    approval = service.record_approval_decision(
        case_id=test_data["case"].id,
        recommendation_id=test_data["recommendation"].id,
        decided_by_user_id=test_data["user"].id,
        decision_code="approved",
        rationale_text="Time critical, approve"
    )
    
    assert approval is not None
    assert approval.case_id == test_data["case"].id
    assert approval.recommendation_id == test_data["recommendation"].id
    assert approval.decided_by_user_id == test_data["user"].id
    assert approval.decision_code == "approved"
    assert approval.rationale_text == "Time critical, approve"
    assert approval.decision_version == 1


def test_record_approval_rejected(db_session, test_data):
    """Test recording a rejected decision."""
    service = ApprovalService(db_session)
    
    approval = service.record_approval_decision(
        case_id=test_data["case"].id,
        recommendation_id=test_data["recommendation"].id,
        decided_by_user_id=test_data["user"].id,
        decision_code="rejected",
        rationale_text="Insufficient evidence"
    )
    
    assert approval is not None
    assert approval.decision_code == "rejected"
    assert approval.rationale_text == "Insufficient evidence"
    assert approval.decision_version == 1


def test_record_approval_invalid_decision_code(db_session, test_data):
    """Test that invalid decision code raises error."""
    service = ApprovalService(db_session)
    
    with pytest.raises(ValueError, match="Invalid decision_code"):
        service.record_approval_decision(
            case_id=test_data["case"].id,
            recommendation_id=test_data["recommendation"].id,
            decided_by_user_id=test_data["user"].id,
            decision_code="invalid_code",
            rationale_text="Test"
        )


def test_record_approval_case_not_found(db_session, test_data):
    """Test that nonexistent case raises error."""
    service = ApprovalService(db_session)
    
    with pytest.raises(ValueError, match="Case .* not found"):
        service.record_approval_decision(
            case_id=str(uuid.uuid4()),
            recommendation_id=test_data["recommendation"].id,
            decided_by_user_id=test_data["user"].id,
            decision_code="approved"
        )


def test_record_approval_recommendation_not_found(db_session, test_data):
    """Test that nonexistent recommendation raises error."""
    service = ApprovalService(db_session)
    
    with pytest.raises(ValueError, match="Recommendation .* not found"):
        service.record_approval_decision(
            case_id=test_data["case"].id,
            recommendation_id=str(uuid.uuid4()),
            decided_by_user_id=test_data["user"].id,
            decision_code="approved"
        )


def test_is_approved(db_session, test_data):
    """Test is_approved check."""
    service = ApprovalService(db_session)
    
    # Initially not approved
    assert not service.is_approved(test_data["case"].id, test_data["recommendation"].id)
    
    # Record approval
    service.record_approval_decision(
        case_id=test_data["case"].id,
        recommendation_id=test_data["recommendation"].id,
        decided_by_user_id=test_data["user"].id,
        decision_code="approved"
    )
    
    # Now approved
    assert service.is_approved(test_data["case"].id, test_data["recommendation"].id)


def test_decision_version_increment(db_session, test_data):
    """Test that decision_version increments on subsequent decisions."""
    service = ApprovalService(db_session)
    
    # First decision
    approval1 = service.record_approval_decision(
        case_id=test_data["case"].id,
        recommendation_id=test_data["recommendation"].id,
        decided_by_user_id=test_data["user"].id,
        decision_code="rejected",
        rationale_text="Need more info"
    )
    assert approval1.decision_version == 1
    
    # Second decision (after getting more info)
    approval2 = service.record_approval_decision(
        case_id=test_data["case"].id,
        recommendation_id=test_data["recommendation"].id,
        decided_by_user_id=test_data["user"].id,
        decision_code="approved",
        rationale_text="Info provided, approve"
    )
    assert approval2.decision_version == 2
    
    # Latest decision should be approved
    assert service.is_approved(test_data["case"].id, test_data["recommendation"].id)
