"""Task repository for task management."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.task import Task


class TaskRepository:
    """Repository for task access and status management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, task_id: str) -> Task | None:
        """Get task by ID."""
        return self.db.get(Task, task_id)
    
    def list_by_case(self, case_id: str) -> list[Task]:
        """
        Get all tasks for a case.
        
        Args:
            case_id: Exception case ID
        
        Returns:
            List of Task records ordered by created_at descending
        """
        stmt = (
            select(Task)
            .where(Task.case_id == case_id)
            .order_by(Task.created_at.desc())
        )
        
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def list_by_status(
        self,
        status_code: str,
        assigned_role_code: str | None = None,
        assigned_partner_org_code: str | None = None
    ) -> list[Task]:
        """
        Get tasks by status with optional role/org filtering.
        
        Args:
            status_code: Task status (assigned, acknowledged, in_progress, completed)
            assigned_role_code: Optional role filter
            assigned_partner_org_code: Optional partner org filter
        
        Returns:
            List of Task records ordered by deadline_at ascending
        """
        stmt = select(Task).where(Task.status_code == status_code)
        
        if assigned_role_code:
            stmt = stmt.where(Task.assigned_role_code == assigned_role_code)
        
        if assigned_partner_org_code:
            stmt = stmt.where(Task.assigned_partner_org_code == assigned_partner_org_code)
        
        stmt = stmt.order_by(Task.deadline_at.asc())
        
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def create(
        self,
        case_id: str,
        recommendation_id: str,
        assigned_role_code: str,
        assigned_partner_org_code: str | None,
        bag_reference: str,
        station_code: str,
        flight_context_text: str,
        instruction_text: str,
        evidence_links_json: str,
        deadline_at: datetime,
        status_code: str = "assigned"
    ) -> Task:
        """
        Create a new task.
        
        Args:
            case_id: Exception case ID
            recommendation_id: Recommendation ID
            assigned_role_code: Role code (operations, partner)
            assigned_partner_org_code: Partner org code if partner role
            bag_reference: Bag tag reference
            station_code: Station code
            flight_context_text: Flight context description
            instruction_text: Task instructions
            evidence_links_json: Evidence links as JSON string
            deadline_at: Task deadline timestamp
            status_code: Initial status (default: assigned)
        
        Returns:
            Created Task
        """
        task = Task(
            id=str(uuid.uuid4()),
            case_id=case_id,
            recommendation_id=recommendation_id,
            assigned_role_code=assigned_role_code,
            assigned_partner_org_code=assigned_partner_org_code,
            bag_reference=bag_reference,
            station_code=station_code,
            flight_context_text=flight_context_text,
            instruction_text=instruction_text,
            evidence_links_json=evidence_links_json,
            deadline_at=deadline_at,
            status_code=status_code,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def update_status(self, task_id: str, status_code: str) -> Task | None:
        """
        Update task status.
        
        Args:
            task_id: Task ID
            status_code: New status code
        
        Returns:
            Updated Task or None if not found
        """
        task = self.get_by_id(task_id)
        if not task:
            return None
        
        task.status_code = status_code
        task.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def list_by_partner_org_and_role(
        self,
        partner_org_code: str,
        assigned_role_code: str = "partner",
        status_code: str | None = None
    ) -> list[Task]:
        """
        Get tasks for a specific partner organization with least-privilege query.
        
        Implements FR-009: partner role-scoped work queue with separation from internal notes.
        Returns tasks assigned to the partner organization only.
        
        Args:
            partner_org_code: Partner organization code (e.g., DNATA, Menzies)
            assigned_role_code: Role code (default: partner)
            status_code: Optional status filter (assigned, acknowledged, in_progress, completed)
        
        Returns:
            List of Task records ordered by deadline_at ascending
        """
        stmt = (
            select(Task)
            .where(Task.assigned_partner_org_code == partner_org_code)
            .where(Task.assigned_role_code == assigned_role_code)
        )
        
        if status_code:
            stmt = stmt.where(Task.status_code == status_code)
        
        stmt = stmt.order_by(Task.deadline_at.asc())
        
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_id_with_partner_scope(
        self,
        task_id: str,
        partner_org_code: str
    ) -> Task | None:
        """
        Get task by ID with partner organization scope enforcement.
        
        Implements REQ-API-005: returns 403 FORBIDDEN_SCOPE if task.assigned_partner_org_code
        does not match current_user.partner_org_code.
        
        Args:
            task_id: Task ID
            partner_org_code: Current user's partner organization code
        
        Returns:
            Task if found and org matches, None if not found or org mismatch
        """
        task = self.get_by_id(task_id)
        
        if not task:
            return None
        
        # Enforce partner org scope: task must be assigned to user's org
        if task.assigned_partner_org_code != partner_org_code:
            # Return None to signal 403 FORBIDDEN_SCOPE
            return None
        
        return task
