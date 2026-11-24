"""Task evidence repository for task evidence management."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models.task import TaskEvidence


class TaskEvidenceRepository:
    """Repository for task evidence access and creation with idempotent replay support."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, evidence_id: str) -> TaskEvidence | None:
        """Get task evidence by ID."""
        return self.db.get(TaskEvidence, evidence_id)
    
    def list_by_task(self, task_id: str) -> list[TaskEvidence]:
        """
        Get all evidence for a task ordered by recorded_at descending.
        
        Args:
            task_id: Task ID
        
        Returns:
            List of TaskEvidence records ordered by recorded_at descending
        """
        stmt = (
            select(TaskEvidence)
            .where(TaskEvidence.task_id == task_id)
            .order_by(TaskEvidence.recorded_at.desc())
        )
        
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def create(
        self,
        task_id: str,
        actor_user_id: str,
        event_type: str,
        note_text: str | None,
        evidence_type: str | None,
        evidence_reference: str | None,
        client_event_id: str
    ) -> TaskEvidence | None:
        """
        Create a new task evidence record with idempotent replay support.
        
        Uses unique constraint on client_event_id to prevent duplicate evidence
        submissions during idempotent replay. If client_event_id already exists,
        returns None instead of raising an error.
        
        Args:
            task_id: Task ID
            actor_user_id: User ID of actor submitting evidence
            event_type: Event type (acknowledged, in_progress, completed, evidence_submitted, blocked)
            note_text: Optional note text
            evidence_type: Optional evidence type (scan_confirmation, handover_proof, completion_note)
            evidence_reference: Optional evidence reference identifier
            client_event_id: Client-provided idempotency key (must be unique)
        
        Returns:
            Created TaskEvidence or None if client_event_id already exists (idempotent replay)
        """
        evidence = TaskEvidence(
            id=str(uuid.uuid4()),
            task_id=task_id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            note_text=note_text,
            evidence_type=evidence_type,
            evidence_reference=evidence_reference,
            client_event_id=client_event_id,
            recorded_at=datetime.now(timezone.utc)
        )
        
        try:
            self.db.add(evidence)
            self.db.commit()
            self.db.refresh(evidence)
            return evidence
        except IntegrityError:
            # Idempotent replay: client_event_id already exists
            self.db.rollback()
            return None
