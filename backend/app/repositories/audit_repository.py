"""Audit event repository."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models.audit import AuditEvent


class AuditRepository:
    """Repository for audit event persistence."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_audit_event(
        self,
        actor_user_id: str | None,
        action_type: str,
        entity_type: str,
        entity_id: str,
        correlation_id: str,
        outcome_code: str,
        detail_json: str,
        occurred_at: datetime | None = None,
    ) -> AuditEvent:
        """
        Create a new audit event record (append-only).
        
        Args:
            actor_user_id: User ID of the actor (nullable for system actions)
            action_type: Type of action (e.g., login_success, approval_decision, task_evidence_submitted)
            entity_type: Type of entity affected (e.g., user, exception_case, task)
            entity_id: ID of the affected entity
            correlation_id: Request correlation ID for tracing
            outcome_code: Outcome of the action (e.g., success, failure, denied)
            detail_json: JSON payload with additional context
            occurred_at: Timestamp of the event (defaults to now)
        
        Returns:
            Created AuditEvent instance
        """
        event = AuditEvent(
            id=str(uuid.uuid4()),
            actor_user_id=actor_user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
            outcome_code=outcome_code,
            detail_json=detail_json,
            occurred_at=occurred_at or datetime.now(timezone.utc),
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def get_events_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50
    ) -> list[AuditEvent]:
        """
        Retrieve audit events for a specific entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of the entity
            limit: Maximum number of events to return
        
        Returns:
            List of AuditEvent instances, ordered by most recent first
        """
        return (
            self.db.query(AuditEvent)
            .filter(
                AuditEvent.entity_type == entity_type,
                AuditEvent.entity_id == entity_id
            )
            .order_by(AuditEvent.occurred_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_events_by_correlation_id(self, correlation_id: str) -> list[AuditEvent]:
        """
        Retrieve all audit events for a specific correlation ID.
        Useful for tracing a full request flow.
        
        Args:
            correlation_id: Request correlation ID
        
        Returns:
            List of AuditEvent instances, ordered chronologically
        """
        return (
            self.db.query(AuditEvent)
            .filter(AuditEvent.correlation_id == correlation_id)
            .order_by(AuditEvent.occurred_at.asc())
            .all()
        )
    
    def get_events_by_actor(
        self,
        actor_user_id: str,
        limit: int = 50
    ) -> list[AuditEvent]:
        """
        Retrieve audit events by actor user ID.
        
        Args:
            actor_user_id: User ID of the actor
            limit: Maximum number of events to return
        
        Returns:
            List of AuditEvent instances, ordered by most recent first
        """
        return (
            self.db.query(AuditEvent)
            .filter(AuditEvent.actor_user_id == actor_user_id)
            .order_by(AuditEvent.occurred_at.desc())
            .limit(limit)
            .all()
        )
