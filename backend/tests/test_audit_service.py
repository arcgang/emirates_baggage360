"""Tests for audit service and correlation ID propagation."""
import pytest
import json
from datetime import datetime, timezone
from app.services.audit_service import AuditService
from app.models.audit import AuditEvent


def test_record_audit_event(db_session):
    """Test recording an audit event with all required fields."""
    service = AuditService(db_session)
    
    service.record_audit_event(
        actor_user_id="user-123",
        action_type="login_success",
        entity_type="user",
        entity_id="user-123",
        correlation_id="corr-123",
        outcome_code="success",
        detail_json={"email": "test@example.com", "role": "operations"}
    )
    
    # Verify event was persisted
    event = db_session.query(AuditEvent).filter(AuditEvent.correlation_id == "corr-123").first()
    assert event is not None
    assert event.actor_user_id == "user-123"
    assert event.action_type == "login_success"
    assert event.entity_type == "user"
    assert event.entity_id == "user-123"
    assert event.outcome_code == "success"
    assert event.correlation_id == "corr-123"
    
    detail = json.loads(event.detail_json)
    assert detail["email"] == "test@example.com"
    assert detail["role"] == "operations"


def test_record_audit_event_nullable_actor(db_session):
    """Test recording system audit event with nullable actor_user_id."""
    service = AuditService(db_session)
    
    service.record_audit_event(
        actor_user_id=None,
        action_type="login_failure",
        entity_type="user",
        entity_id="unknown",
        correlation_id="corr-456",
        outcome_code="failure",
        detail_json={"reason": "invalid_credentials"}
    )
    
    event = db_session.query(AuditEvent).filter(AuditEvent.correlation_id == "corr-456").first()
    assert event is not None
    assert event.actor_user_id is None
    assert event.action_type == "login_failure"
    assert event.outcome_code == "failure"


def test_get_audit_trail_for_case(db_session):
    """Test retrieving audit trail for a specific case."""
    service = AuditService(db_session)
    
    # Record multiple events for a case
    case_id = "case-789"
    service.record_audit_event(
        actor_user_id="user-123",
        action_type="case_created",
        entity_type="exception_case",
        entity_id=case_id,
        correlation_id="corr-789-1",
        outcome_code="success",
        detail_json={"severity": "critical"}
    )
    
    service.record_audit_event(
        actor_user_id="user-456",
        action_type="approval_decision_approved",
        entity_type="exception_case",
        entity_id=case_id,
        correlation_id="corr-789-2",
        outcome_code="success",
        detail_json={"recommendation_id": "rec-123"}
    )
    
    # Retrieve audit trail
    trail = service.get_audit_trail_for_case(case_id)
    assert len(trail) == 2
    assert trail[0]["action_type"] == "approval_decision_approved"  # Most recent first
    assert trail[1]["action_type"] == "case_created"
    assert trail[0]["entity_id"] == case_id
    assert trail[1]["entity_id"] == case_id


def test_trace_by_correlation_id(db_session):
    """Test tracing audit events by correlation ID."""
    service = AuditService(db_session)
    
    correlation_id = "corr-trace-123"
    
    # Record multiple events with same correlation ID
    service.record_audit_event(
        actor_user_id="user-123",
        action_type="case_created",
        entity_type="exception_case",
        entity_id="case-1",
        correlation_id=correlation_id,
        outcome_code="success",
        detail_json={}
    )
    
    service.record_audit_event(
        actor_user_id="user-123",
        action_type="approval_decision_approved",
        entity_type="approval_decision",
        entity_id="approval-1",
        correlation_id=correlation_id,
        outcome_code="success",
        detail_json={}
    )
    
    service.record_audit_event(
        actor_user_id="user-456",
        action_type="task_evidence_submitted",
        entity_type="task",
        entity_id="task-1",
        correlation_id=correlation_id,
        outcome_code="success",
        detail_json={}
    )
    
    # Trace by correlation ID
    trace = service.trace_by_correlation_id(correlation_id)
    assert len(trace) == 3
    assert trace[0]["action_type"] == "case_created"  # Chronological order
    assert trace[1]["action_type"] == "approval_decision_approved"
    assert trace[2]["action_type"] == "task_evidence_submitted"
    assert all(event["correlation_id"] == correlation_id for event in trace)


def test_audit_event_detail_json_parsing(db_session):
    """Test that detail_json is correctly serialized and deserialized."""
    service = AuditService(db_session)
    
    detail_data = {
        "case_reference": "BC-DXB-240611",
        "severity": "critical",
        "bag_count": 3,
        "nested": {"key": "value"}
    }
    
    service.record_audit_event(
        actor_user_id="user-123",
        action_type="case_created",
        entity_type="exception_case",
        entity_id="case-123",
        correlation_id="corr-json-test",
        outcome_code="success",
        detail_json=detail_data
    )
    
    trail = service.get_audit_trail_for_case("case-123")
    assert len(trail) == 1
    assert trail[0]["detail"] == detail_data
    assert trail[0]["detail"]["nested"]["key"] == "value"


def test_correlation_id_propagation(db_session):
    """Test that correlation IDs enable end-to-end tracing across actions."""
    service = AuditService(db_session)
    
    # Simulate a full flow with one correlation ID
    correlation_id = "flow-corr-123"
    
    # Step 1: Case created
    service.record_audit_event(
        actor_user_id="ops-user",
        action_type="case_created",
        entity_type="exception_case",
        entity_id="case-flow-1",
        correlation_id=correlation_id,
        outcome_code="success",
        detail_json={"step": 1}
    )
    
    # Step 2: Approval decision
    service.record_audit_event(
        actor_user_id="ops-user",
        action_type="approval_decision_approved",
        entity_type="approval_decision",
        entity_id="approval-flow-1",
        correlation_id=correlation_id,
        outcome_code="success",
        detail_json={"step": 2}
    )
    
    # Step 3: Task created (implicit, not audited here but would share correlation_id)
    # Step 4: Evidence submitted
    service.record_audit_event(
        actor_user_id="partner-user",
        action_type="task_evidence_submitted",
        entity_type="task",
        entity_id="task-flow-1",
        correlation_id=correlation_id,
        outcome_code="success",
        detail_json={"step": 4}
    )
    
    # Step 5: Case closed
    service.record_audit_event(
        actor_user_id="ops-user",
        action_type="case_closed",
        entity_type="exception_case",
        entity_id="case-flow-1",
        correlation_id=correlation_id,
        outcome_code="success",
        detail_json={"step": 5}
    )
    
    # Trace the full flow
    trace = service.trace_by_correlation_id(correlation_id)
    assert len(trace) == 4
    assert trace[0]["detail"]["step"] == 1
    assert trace[1]["detail"]["step"] == 2
    assert trace[2]["detail"]["step"] == 4
    assert trace[3]["detail"]["step"] == 5
    
    # Verify different actors but same correlation ID
    assert trace[0]["actor_user_id"] == "ops-user"
    assert trace[2]["actor_user_id"] == "partner-user"
    assert trace[3]["actor_user_id"] == "ops-user"
