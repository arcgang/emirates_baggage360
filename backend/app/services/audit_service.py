"""Audit trail service for security-relevant and operationally relevant actions."""
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..repositories.audit_repository import AuditRepository


class AuditService:
    """
    Service for recording audit events.
    Implements FR-016: Case audit trail with actor, action, timestamp, and entity context.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuditRepository(db)
    
    def record_audit_event(
        self,
        actor_user_id: str | None,
        action_type: str,
        entity_type: str,
        entity_id: str,
        correlation_id: str,
        outcome_code: str,
        detail_json: dict | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        """
        Record an audit event (append-only).
        
        Args:
            actor_user_id: User ID of the actor performing the action (nullable for system actions)
            action_type: Type of action being audited
                Examples:
                - login_success, login_failure
                - approval_decision_approved, approval_decision_rejected
                - task_evidence_submitted
                - case_created, case_closed
                - recommendation_generated
            entity_type: Type of entity being acted upon
                Examples: user, exception_case, approval_decision, task, recommendation
            entity_id: ID of the entity
            correlation_id: Request correlation ID for end-to-end tracing
            outcome_code: Outcome of the action (success, failure, denied, etc.)
            detail_json: Optional JSON payload with additional context
            occurred_at: Timestamp of the event (defaults to now)
        
        Returns:
            None (audit events are fire-and-forget)
        """
        detail_payload = json.dumps(detail_json) if detail_json else "{}"
        
        self.repo.create_audit_event(
            actor_user_id=actor_user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
            outcome_code=outcome_code,
            detail_json=detail_payload,
            occurred_at=occurred_at,
        )
    
    def get_audit_trail_for_case(self, case_id: str, limit: int = 50) -> list[dict]:
        """
        Retrieve audit trail for an exception case.
        Returns events related to the case and its child entities (recommendations, approvals, tasks).
        
        Args:
            case_id: Exception case ID
            limit: Maximum number of events to return
        
        Returns:
            List of audit event dictionaries
        """
        events = self.repo.get_events_by_entity(
            entity_type="exception_case",
            entity_id=case_id,
            limit=limit
        )
        
        return [
            {
                "audit_event_id": event.id,
                "actor_user_id": event.actor_user_id,
                "action_type": event.action_type,
                "entity_type": event.entity_type,
                "entity_id": event.entity_id,
                "correlation_id": event.correlation_id,
                "outcome_code": event.outcome_code,
                "detail": json.loads(event.detail_json) if event.detail_json else {},
                "occurred_at": event.occurred_at,
            }
            for event in events
        ]
    
    def trace_by_correlation_id(self, correlation_id: str) -> list[dict]:
        """
        Trace all audit events for a request correlation ID.
        Useful for following a full recommendation → approval → task → completion flow.
        
        Args:
            correlation_id: Request correlation ID
        
        Returns:
            List of audit event dictionaries in chronological order
        """
        events = self.repo.get_events_by_correlation_id(correlation_id)
        
        return [
            {
                "audit_event_id": event.id,
                "actor_user_id": event.actor_user_id,
                "action_type": event.action_type,
                "entity_type": event.entity_type,
                "entity_id": event.entity_id,
                "correlation_id": event.correlation_id,
                "outcome_code": event.outcome_code,
                "detail": json.loads(event.detail_json) if event.detail_json else {},
                "occurred_at": event.occurred_at,
            }
            for event in events
        ]
