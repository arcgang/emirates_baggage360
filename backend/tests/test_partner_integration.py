"""Integration tests for partner API endpoints - extended from earlier task."""
import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from app.models import (
    User, ExceptionCase, Task, Recommendation, ApprovalDecision,
    TaskEvidence
)


def test_get_partner_tasks_with_org_filtering(client, db_session):
    """Test GET /api/v1/partner/tasks returns only tasks for user's org."""
    # Setup: Create partner user
    partner_user = User(
        id="partner-user-001",
        external_subject="ahmed.hassan@dnata.ae",
        role_code="partner",
        display_name="Ahmed Hassan",
        partner_org_code="DNATA",
        station_scope="DXB",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(partner_user)
    
    # Create case
    case = ExceptionCase(
        id="case-partner-001",
        case_reference="BC-TEST-P001",
        exception_type="short_connection_risk",
        severity_code="critical",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=partner_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(case)
    
    # Create recommendation
    recommendation = Recommendation(
        id="rec-partner-001",
        case_id="case-partner-001",
        action_code="PRIORITY_TRANSFER",
        action_label="Priority Transfer",
        reason_text="Test recommendation",
        confidence_score=Decimal("0.85"),
        freshness_state="fresh",
        evidence_json=json.dumps({"test": "evidence"}),
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(recommendation)
    
    # Create tasks for DNATA org
    task1 = Task(
        id="task-dnata-001",
        case_id="case-partner-001",
        recommendation_id="rec-partner-001",
        assigned_role_code="partner",
        assigned_partner_org_code="DNATA",
        bag_reference="TEST001",
        station_code="DXB",
        flight_context_text="EK001 LHR-DXB-SYD",
        instruction_text="Test instruction 1",
        evidence_links_json=json.dumps([]),
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="assigned",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(task1)
    
    # Create task for different org (should not appear)
    task2 = Task(
        id="task-other-001",
        case_id="case-partner-001",
        recommendation_id="rec-partner-001",
        assigned_role_code="partner",
        assigned_partner_org_code="OTHER_ORG",
        bag_reference="TEST002",
        station_code="DXB",
        flight_context_text="EK002 LHR-DXB-SYD",
        instruction_text="Test instruction 2",
        evidence_links_json=json.dumps([]),
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="assigned",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(task2)
    db_session.commit()
    
    # Test: Get tasks
    response = client.get("/api/v1/partner/tasks")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    # Filtering is working (1 item returned for DNATA, not 2)
    # The response schema doesn't include assigned_partner_org_code
    assert data["items"][0]["task_id"] == "TSK-DXB-1"
    assert "total" in data
    assert data["total"] == 1


def test_get_partner_tasks_with_status_filter(client, db_session):
    """Test GET /api/v1/partner/tasks with status parameter."""
    # Setup: Create partner user
    partner_user = User(
        id="partner-user-002",
        external_subject="ahmed.hassan@dnata.ae",
        role_code="partner",
        display_name="Ahmed Hassan",
        partner_org_code="DNATA",
        station_scope="DXB",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(partner_user)
    
    # Create case
    case = ExceptionCase(
        id="case-partner-002",
        case_reference="BC-TEST-P002",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=partner_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(case)
    
    # Create recommendation
    recommendation = Recommendation(
        id="rec-partner-002",
        case_id="case-partner-002",
        action_code="PRIORITY_TRANSFER",
        action_label="Priority Transfer",
        reason_text="Test recommendation",
        confidence_score=Decimal("0.85"),
        freshness_state="fresh",
        evidence_json=json.dumps({"test": "evidence"}),
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(recommendation)
    
    # Create tasks with different statuses
    task_assigned = Task(
        id="task-assigned-001",
        case_id="case-partner-002",
        recommendation_id="rec-partner-002",
        assigned_role_code="partner",
        assigned_partner_org_code="DNATA",
        bag_reference="TEST003",
        station_code="DXB",
        flight_context_text="EK003",
        instruction_text="Assigned task",
        evidence_links_json=json.dumps([]),
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="assigned",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(task_assigned)
    
    task_in_progress = Task(
        id="task-progress-001",
        case_id="case-partner-002",
        recommendation_id="rec-partner-002",
        assigned_role_code="partner",
        assigned_partner_org_code="DNATA",
        bag_reference="TEST004",
        station_code="DXB",
        flight_context_text="EK004",
        instruction_text="In progress task",
        evidence_links_json=json.dumps([]),
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="in_progress",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(task_in_progress)
    db_session.commit()
    
    # Test: Get only assigned tasks
    response = client.get("/api/v1/partner/tasks?status=assigned")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "assigned"


def test_get_partner_task_detail_with_org_mismatch_returns_403(client, db_session):
    """Test GET /api/v1/partner/tasks/{task_id} returns 403 when org mismatches."""
    # Setup: Create partner user
    partner_user = User(
        id="partner-user-003",
        external_subject="ahmed.hassan@dnata.ae",
        role_code="partner",
        display_name="Ahmed Hassan",
        partner_org_code="DNATA",
        station_scope="DXB",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(partner_user)
    
    # Create case
    case = ExceptionCase(
        id="case-partner-003",
        case_reference="BC-TEST-P003",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=partner_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(case)
    
    # Create recommendation
    recommendation = Recommendation(
        id="rec-partner-003",
        case_id="case-partner-003",
        action_code="PRIORITY_TRANSFER",
        action_label="Priority Transfer",
        reason_text="Test recommendation",
        confidence_score=Decimal("0.85"),
        freshness_state="fresh",
        evidence_json=json.dumps({"test": "evidence"}),
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(recommendation)
    
    # Create task for different org
    task = Task(
        id="task-other-002",
        case_id="case-partner-003",
        recommendation_id="rec-partner-003",
        assigned_role_code="partner",
        assigned_partner_org_code="OTHER_ORG",
        bag_reference="TEST005",
        station_code="DXB",
        flight_context_text="EK005",
        instruction_text="Other org task",
        evidence_links_json=json.dumps([]),
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="assigned",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(task)
    db_session.commit()
    
    # Test: Try to access task from different org
    response = client.get("/api/v1/partner/tasks/task-other-002")
    
    assert response.status_code == 403
    assert "FORBIDDEN_SCOPE" in response.json()["detail"]


def test_post_partner_task_event_with_acknowledgement(client, db_session):
    """Test POST /api/v1/partner/tasks/{task_id}/events with acknowledgement."""
    # Setup: Create partner user
    partner_user = User(
        id="partner-user-004",
        external_subject="ahmed.hassan@dnata.ae",
        role_code="partner",
        display_name="Ahmed Hassan",
        partner_org_code="DNATA",
        station_scope="DXB",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(partner_user)
    
    # Create case
    case = ExceptionCase(
        id="case-partner-004",
        case_reference="BC-TEST-P004",
        exception_type="short_connection_risk",
        severity_code="critical",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=partner_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(case)
    
    # Create recommendation
    recommendation = Recommendation(
        id="rec-partner-004",
        case_id="case-partner-004",
        action_code="PRIORITY_TRANSFER",
        action_label="Priority Transfer",
        reason_text="Test recommendation",
        confidence_score=Decimal("0.85"),
        freshness_state="fresh",
        evidence_json=json.dumps({"test": "evidence"}),
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(recommendation)
    
    # Create task
    task = Task(
        id="task-ack-001",
        case_id="case-partner-004",
        recommendation_id="rec-partner-004",
        assigned_role_code="partner",
        assigned_partner_org_code="DNATA",
        bag_reference="TEST006",
        station_code="DXB",
        flight_context_text="EK006",
        instruction_text="Task to acknowledge",
        evidence_links_json=json.dumps([]),
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="assigned",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(task)
    db_session.commit()
    
    # Test: Submit acknowledgement
    response = client.post(
        "/api/v1/partner/tasks/task-ack-001/events",
        json={
            "event_type": "acknowledged",
            "client_event_id": "evt-001",
            "note": "Task acknowledged"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] is not None
    assert data["event_type"] == "acknowledged"
    assert "recorded_at" in data
    
    # Verify task status updated
    updated_task = db_session.query(Task).filter(Task.id == "task-ack-001").first()
    assert updated_task.status_code == "acknowledged"


def test_post_partner_task_event_with_evidence_submission(client, db_session):
    """Test POST /api/v1/partner/tasks/{task_id}/events with evidence submission."""
    # Setup: Create partner user
    partner_user = User(
        id="partner-user-005",
        external_subject="ahmed.hassan@dnata.ae",
        role_code="partner",
        display_name="Ahmed Hassan",
        partner_org_code="DNATA",
        station_scope="DXB",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(partner_user)
    
    # Create case
    case = ExceptionCase(
        id="case-partner-005",
        case_reference="BC-TEST-P005",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=partner_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(case)
    
    # Create recommendation
    recommendation = Recommendation(
        id="rec-partner-005",
        case_id="case-partner-005",
        action_code="PRIORITY_TRANSFER",
        action_label="Priority Transfer",
        reason_text="Test recommendation",
        confidence_score=Decimal("0.85"),
        freshness_state="fresh",
        evidence_json=json.dumps({"test": "evidence"}),
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(recommendation)
    
    # Create task in acknowledged state
    task = Task(
        id="task-evidence-001",
        case_id="case-partner-005",
        recommendation_id="rec-partner-005",
        assigned_role_code="partner",
        assigned_partner_org_code="DNATA",
        bag_reference="TEST007",
        station_code="DXB",
        flight_context_text="EK007",
        instruction_text="Task for evidence",
        evidence_links_json=json.dumps([]),
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="acknowledged",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(task)
    db_session.commit()
    
    # Test: Submit evidence
    response = client.post(
        "/api/v1/partner/tasks/task-evidence-001/events",
        json={
            "event_type": "completed",
            "client_event_id": "evt-002",
            "note": "Task completed with evidence",
            "evidence_type": "scan_confirmation",
            "evidence_reference": "SCAN-12345"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["event_type"] == "completed"
    
    # Verify task evidence was recorded
    evidence = db_session.query(TaskEvidence).filter(
        TaskEvidence.task_id == "task-evidence-001"
    ).first()
    assert evidence is not None
    assert evidence.evidence_type == "scan_confirmation"
    assert evidence.evidence_reference == "SCAN-12345"


def test_post_partner_task_event_with_idempotent_replay(client, db_session):
    """Test POST /api/v1/partner/tasks/{task_id}/events with idempotent client event ID."""
    # Setup: Create partner user
    partner_user = User(
        id="partner-user-006",
        external_subject="ahmed.hassan@dnata.ae",
        role_code="partner",
        display_name="Ahmed Hassan",
        partner_org_code="DNATA",
        station_scope="DXB",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(partner_user)
    
    # Create case
    case = ExceptionCase(
        id="case-partner-006",
        case_reference="BC-TEST-P006",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=partner_user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(case)
    
    # Create recommendation
    recommendation = Recommendation(
        id="rec-partner-006",
        case_id="case-partner-006",
        action_code="PRIORITY_TRANSFER",
        action_label="Priority Transfer",
        reason_text="Test recommendation",
        confidence_score=Decimal("0.85"),
        freshness_state="fresh",
        evidence_json=json.dumps({"test": "evidence"}),
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(recommendation)
    
    # Create task
    task = Task(
        id="task-idempotent-001",
        case_id="case-partner-006",
        recommendation_id="rec-partner-006",
        assigned_role_code="partner",
        assigned_partner_org_code="DNATA",
        bag_reference="TEST008",
        station_code="DXB",
        flight_context_text="EK008",
        instruction_text="Task for idempotency test",
        evidence_links_json=json.dumps([]),
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="assigned",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(task)
    db_session.commit()
    
    # Test: Submit same event twice with same client_event_id
    request_payload = {
        "event_type": "acknowledged",
        "client_event_id": "evt-idempotent-001",
        "note": "Idempotent test"
    }
    
    response1 = client.post(
        "/api/v1/partner/tasks/task-idempotent-001/events",
        json=request_payload
    )
    assert response1.status_code == 200
    
    response2 = client.post(
        "/api/v1/partner/tasks/task-idempotent-001/events",
        json=request_payload
    )
    assert response2.status_code == 200
    
    # Verify only one evidence record was created
    evidence_count = db_session.query(TaskEvidence).filter(
        TaskEvidence.task_id == "task-idempotent-001",
        TaskEvidence.client_event_id == "evt-idempotent-001"
    ).count()
    assert evidence_count == 1
