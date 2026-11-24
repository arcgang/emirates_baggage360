"""Tests for task dispatch service - task event submission and idempotent replay."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.orm import Session

from app.models.task import Task, TaskEvidence
from app.models.user import User
from app.models.exception_case import ExceptionCase
from app.models.recommendation import Recommendation
from app.models.approval import ApprovalDecision
from app.repositories.task_repository import TaskRepository
from app.repositories.task_evidence_repository import TaskEvidenceRepository
from app.services.task_dispatch_service import TaskDispatchService


def test_accept_task_event_acknowledged(db_session: Session):
    """Test task event submission with acknowledged event type."""
    # Create test user
    user = User(
        id=str(uuid.uuid4()),
        external_subject="partner@test.com",
        role_code="partner",
        display_name="Partner User",
        partner_org_code="DNATA",
        active_flag=True
    )
    db_session.add(user)
    
    # Create test case
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="TEST-CASE-001",
        exception_type="short_connection_risk",
        severity_code="critical",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="tasked",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=user.id
    )
    db_session.add(case)
    
    # Create test recommendation
    rec = Recommendation(
        id=str(uuid.uuid4()),
        case_id=case.id,
        action_code="PRIORITY_TRANSFER",
        action_label="Test Action",
        reason_text="Test reason",
        confidence_score=0.85,
        freshness_state="fresh",
        evidence_json="{}",
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(rec)
    
    # Create test task
    task = Task(
        id=str(uuid.uuid4()),
        case_id=case.id,
        recommendation_id=rec.id,
        assigned_role_code="partner",
        assigned_partner_org_code="DNATA",
        bag_reference="TEST-BAG-001",
        station_code="DXB",
        flight_context_text="Test flight context",
        instruction_text="Test instructions",
        evidence_links_json="[]",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="assigned"
    )
    db_session.add(task)
    db_session.commit()
    
    # Accept task event
    service = TaskDispatchService(db_session)
    evidence, updated_task, case_status = service.accept_task_event(
        task_id=task.id,
        actor_user_id=user.id,
        event_type="acknowledged",
        note_text="Task acknowledged, proceeding to gate",
        evidence_type="scan_confirmation",
        evidence_reference="SCAN-TEST-001",
        client_event_id="CLIENT-EVT-TEST-001"
    )
    
    # Verify evidence created
    assert evidence is not None
    assert evidence.task_id == task.id
    assert evidence.actor_user_id == user.id
    assert evidence.event_type == "acknowledged"
    assert evidence.note_text == "Task acknowledged, proceeding to gate"
    assert evidence.evidence_type == "scan_confirmation"
    assert evidence.evidence_reference == "SCAN-TEST-001"
    assert evidence.client_event_id == "CLIENT-EVT-TEST-001"
    
    # Verify task status updated
    assert updated_task.status_code == "acknowledged"
    
    # Verify case status (should stay tasked, not all tasks completed)
    assert case_status == "tasked"


def test_accept_task_event_completed_updates_case(db_session: Session):
    """Test that completed task event updates case status (closed if all tasks complete)."""
    # Create test user
    user = User(
        id=str(uuid.uuid4()),
        external_subject="partner@test.com",
        role_code="partner",
        display_name="Partner User",
        partner_org_code="DNATA",
        active_flag=True
    )
    db_session.add(user)
    
    # Create test case
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="TEST-CASE-002",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="tasked",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=user.id
    )
    db_session.add(case)
    
    # Create test recommendation
    rec = Recommendation(
        id=str(uuid.uuid4()),
        case_id=case.id,
        action_code="PRIORITY_TRANSFER",
        action_label="Test Action",
        reason_text="Test reason",
        confidence_score=0.85,
        freshness_state="fresh",
        evidence_json="{}",
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(rec)
    
    # Create test task
    task = Task(
        id=str(uuid.uuid4()),
        case_id=case.id,
        recommendation_id=rec.id,
        assigned_role_code="partner",
        assigned_partner_org_code="DNATA",
        bag_reference="TEST-BAG-002",
        station_code="DXB",
        flight_context_text="Test flight context",
        instruction_text="Test instructions",
        evidence_links_json="[]",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="in_progress"
    )
    db_session.add(task)
    db_session.commit()
    
    # Accept completed event
    service = TaskDispatchService(db_session)
    evidence, updated_task, case_status = service.accept_task_event(
        task_id=task.id,
        actor_user_id=user.id,
        event_type="completed",
        note_text="Bag successfully delivered to gate",
        evidence_type="handover_proof",
        evidence_reference="HANDOVER-TEST-002",
        client_event_id="CLIENT-EVT-TEST-002"
    )
    
    # Verify task status updated to completed
    assert updated_task.status_code == "completed"
    
    # Verify case status updated to closed (since this is the only task and it's completed)
    assert case_status == "closed"


def test_accept_task_event_idempotent_replay(db_session: Session):
    """Test that duplicate client_event_id returns None for idempotent replay."""
    # Create test user
    user = User(
        id=str(uuid.uuid4()),
        external_subject="partner@test.com",
        role_code="partner",
        display_name="Partner User",
        partner_org_code="DNATA",
        active_flag=True
    )
    db_session.add(user)
    
    # Create test case
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="TEST-CASE-003",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="tasked",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=user.id
    )
    db_session.add(case)
    
    # Create test recommendation
    rec = Recommendation(
        id=str(uuid.uuid4()),
        case_id=case.id,
        action_code="PRIORITY_TRANSFER",
        action_label="Test Action",
        reason_text="Test reason",
        confidence_score=0.85,
        freshness_state="fresh",
        evidence_json="{}",
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(rec)
    
    # Create test task
    task = Task(
        id=str(uuid.uuid4()),
        case_id=case.id,
        recommendation_id=rec.id,
        assigned_role_code="partner",
        assigned_partner_org_code="DNATA",
        bag_reference="TEST-BAG-003",
        station_code="DXB",
        flight_context_text="Test flight context",
        instruction_text="Test instructions",
        evidence_links_json="[]",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="assigned"
    )
    db_session.add(task)
    db_session.commit()
    
    # Accept task event first time
    service = TaskDispatchService(db_session)
    evidence1, updated_task1, case_status1 = service.accept_task_event(
        task_id=task.id,
        actor_user_id=user.id,
        event_type="acknowledged",
        note_text="First submission",
        evidence_type=None,
        evidence_reference=None,
        client_event_id="CLIENT-EVT-IDEMPOTENT-TEST"
    )
    
    # Verify first submission created evidence
    assert evidence1 is not None
    assert evidence1.client_event_id == "CLIENT-EVT-IDEMPOTENT-TEST"
    assert updated_task1.status_code == "acknowledged"
    
    # Accept same event again (idempotent replay)
    evidence2, updated_task2, case_status2 = service.accept_task_event(
        task_id=task.id,
        actor_user_id=user.id,
        event_type="acknowledged",
        note_text="Second submission (should be ignored)",
        evidence_type=None,
        evidence_reference=None,
        client_event_id="CLIENT-EVT-IDEMPOTENT-TEST"
    )
    
    # Verify second submission returned None for evidence (idempotent replay detected)
    assert evidence2 is None
    
    # Task status should remain unchanged
    assert updated_task2.status_code == "acknowledged"
    
    # Verify only one evidence record exists
    evidence_repo = TaskEvidenceRepository(db_session)
    all_evidence = evidence_repo.list_by_task(task.id)
    assert len(all_evidence) == 1
    assert all_evidence[0].client_event_id == "CLIENT-EVT-IDEMPOTENT-TEST"
    assert all_evidence[0].note_text == "First submission"


def test_accept_task_event_in_progress(db_session: Session):
    """Test task event submission with in_progress event type."""
    # Create test user
    user = User(
        id=str(uuid.uuid4()),
        external_subject="partner@test.com",
        role_code="partner",
        display_name="Partner User",
        partner_org_code="DNATA",
        active_flag=True
    )
    db_session.add(user)
    
    # Create test case
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="TEST-CASE-004",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="tasked",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=user.id
    )
    db_session.add(case)
    
    # Create test recommendation
    rec = Recommendation(
        id=str(uuid.uuid4()),
        case_id=case.id,
        action_code="PRIORITY_TRANSFER",
        action_label="Test Action",
        reason_text="Test reason",
        confidence_score=0.85,
        freshness_state="fresh",
        evidence_json="{}",
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(rec)
    
    # Create test task
    task = Task(
        id=str(uuid.uuid4()),
        case_id=case.id,
        recommendation_id=rec.id,
        assigned_role_code="partner",
        assigned_partner_org_code="DNATA",
        bag_reference="TEST-BAG-004",
        station_code="DXB",
        flight_context_text="Test flight context",
        instruction_text="Test instructions",
        evidence_links_json="[]",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="acknowledged"
    )
    db_session.add(task)
    db_session.commit()
    
    # Accept in_progress event
    service = TaskDispatchService(db_session)
    evidence, updated_task, case_status = service.accept_task_event(
        task_id=task.id,
        actor_user_id=user.id,
        event_type="in_progress",
        note_text="Bag located, preparing for transfer",
        evidence_type="scan_confirmation",
        evidence_reference="SCAN-TEST-004",
        client_event_id="CLIENT-EVT-TEST-004"
    )
    
    # Verify evidence created
    assert evidence is not None
    assert evidence.event_type == "in_progress"
    
    # Verify task status updated
    assert updated_task.status_code == "in_progress"


def test_accept_task_event_task_not_found(db_session: Session):
    """Test that accept_task_event raises ValueError when task not found."""
    service = TaskDispatchService(db_session)
    
    with pytest.raises(ValueError, match="Task .* not found"):
        service.accept_task_event(
            task_id=str(uuid.uuid4()),
            actor_user_id=str(uuid.uuid4()),
            event_type="acknowledged",
            note_text="Test note",
            evidence_type=None,
            evidence_reference=None,
            client_event_id="CLIENT-EVT-NOT-FOUND"
        )


def test_accept_task_event_all_tasks_completed_closes_case(db_session: Session):
    """Test that when all tasks for a case are completed, case status updates to closed."""
    # Create test user
    user = User(
        id=str(uuid.uuid4()),
        external_subject="partner@test.com",
        role_code="partner",
        display_name="Partner User",
        partner_org_code="DNATA",
        active_flag=True
    )
    db_session.add(user)
    
    # Create test case
    case = ExceptionCase(
        id=str(uuid.uuid4()),
        case_reference="TEST-CASE-005",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="in_recovery",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=user.id
    )
    db_session.add(case)
    
    # Create test recommendation
    rec = Recommendation(
        id=str(uuid.uuid4()),
        case_id=case.id,
        action_code="PRIORITY_TRANSFER",
        action_label="Test Action",
        reason_text="Test reason",
        confidence_score=0.85,
        freshness_state="fresh",
        evidence_json="{}",
        generated_at=datetime.now(timezone.utc)
    )
    db_session.add(rec)
    
    # Create two test tasks - one already completed, one in_progress
    task1 = Task(
        id=str(uuid.uuid4()),
        case_id=case.id,
        recommendation_id=rec.id,
        assigned_role_code="partner",
        assigned_partner_org_code="DNATA",
        bag_reference="TEST-BAG-005A",
        station_code="DXB",
        flight_context_text="Test flight context",
        instruction_text="Test instructions",
        evidence_links_json="[]",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="completed"
    )
    db_session.add(task1)
    
    task2 = Task(
        id=str(uuid.uuid4()),
        case_id=case.id,
        recommendation_id=rec.id,
        assigned_role_code="partner",
        assigned_partner_org_code="DNATA",
        bag_reference="TEST-BAG-005B",
        station_code="DXB",
        flight_context_text="Test flight context",
        instruction_text="Test instructions",
        evidence_links_json="[]",
        deadline_at=datetime.now(timezone.utc) + timedelta(hours=2),
        status_code="in_progress"
    )
    db_session.add(task2)
    db_session.commit()
    
    # Complete the second task
    service = TaskDispatchService(db_session)
    evidence, updated_task, case_status = service.accept_task_event(
        task_id=task2.id,
        actor_user_id=user.id,
        event_type="completed",
        note_text="All tasks completed",
        evidence_type="completion_note",
        evidence_reference="COMPLETE-TEST-005",
        client_event_id="CLIENT-EVT-TEST-005"
    )
    
    # Verify task completed
    assert updated_task.status_code == "completed"
    
    # Verify case status updated to closed
    assert case_status == "closed"
