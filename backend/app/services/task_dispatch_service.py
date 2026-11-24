"""Task dispatch service for creating operational tasks from approved recommendations."""
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models.task import Task, TaskEvidence
from ..repositories.approval_repository import ApprovalRepository
from ..repositories.exception_case_repository import ExceptionCaseRepository
from ..repositories.recommendation_repository import RecommendationRepository
from ..repositories.task_evidence_repository import TaskEvidenceRepository
from ..repositories.task_repository import TaskRepository


class TaskDispatchService:
    """
    Service for operational task dispatch.
    
    Creates tasks for approved recommendations with assigned role,
    partner org, bag reference, station, flight context, instructions,
    evidence links, and deadline.
    
    Enforces FR-007: tasks are only created for approved recommendations.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.approval_repo = ApprovalRepository(db)
        self.case_repo = ExceptionCaseRepository(db)
        self.rec_repo = RecommendationRepository(db)
        self.evidence_repo = TaskEvidenceRepository(db)
    
    def create_tasks_for_approved_recommendation(
        self,
        case_id: str,
        recommendation_id: str
    ) -> list[Task]:
        """
        Generate operational tasks for an approved recommendation.
        
        Validates that the recommendation has been approved before creating tasks.
        Returns 409 conflict error if recommendation not approved.
        
        Task generation logic:
        - PRIORITY_TRANSFER: Create partner task for bag transfer at DXB
        - RESCHEDULE_CONNECTION: Create operations task for rebooking
        - LOCATE_BAG: Create partner task for bag search
        - MONITOR: No task created (monitoring only)
        
        Each task includes:
        - assigned_role_code: operations or partner
        - assigned_partner_org_code: Partner org if partner task
        - bag_reference: Primary bag tag
        - station_code: Operational station (e.g., DXB)
        - flight_context_text: Onward flight context
        - instruction_text: Specific task instructions
        - evidence_links_json: Links to supporting evidence
        - deadline_at: Task deadline (90 minutes before flight departure)
        - status_code: assigned
        
        Args:
            case_id: Exception case ID
            recommendation_id: Recommendation ID
        
        Returns:
            List of created Task objects
        
        Raises:
            ValueError: If case or recommendation not found
            PermissionError: If recommendation not approved (409 conflict)
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        # Verify recommendation exists and belongs to case
        recommendation = self.rec_repo.get_by_id(recommendation_id)
        if not recommendation:
            raise ValueError(f"Recommendation {recommendation_id} not found")
        
        if recommendation.case_id != case_id:
            raise ValueError(f"Recommendation {recommendation_id} does not belong to case {case_id}")
        
        # Verify recommendation is approved
        approval = self.approval_repo.get_by_case_and_recommendation(case_id, recommendation_id)
        if not approval or approval.decision_code != "approved":
            raise PermissionError(
                f"Recommendation {recommendation_id} must be approved before task dispatch. "
                "Current status: " + (approval.decision_code if approval else "no decision")
            )
        
        # Get bags for context
        case_bags = self.case_repo.get_bags_by_case(case_id)
        if not case_bags:
            raise ValueError(f"No bags found for case {case_id}")
        
        # Find primary bag
        primary_bag_id = None
        for cb in case_bags:
            if cb.primary_flag:
                primary_bag_id = cb.bag_id
                break
        if not primary_bag_id:
            primary_bag_id = case_bags[0].bag_id
        
        # Get bag reference from the bag object
        from ..models.bag import Bag
        bag = self.db.query(Bag).filter(Bag.id == primary_bag_id).first()
        if not bag:
            raise ValueError(f"Bag {primary_bag_id} not found")
        bag_reference = bag.bag_tag
        
        # Determine task details based on action code
        tasks = []
        
        if recommendation.action_code == "PRIORITY_TRANSFER":
            task = self._create_priority_transfer_task(
                case_id=case_id,
                recommendation_id=recommendation_id,
                bag_reference=bag_reference,
                deadline_at=case.deadline_at
            )
            tasks.append(task)
        
        elif recommendation.action_code == "RESCHEDULE_CONNECTION":
            task = self._create_reschedule_task(
                case_id=case_id,
                recommendation_id=recommendation_id,
                bag_reference=bag_reference,
                deadline_at=case.deadline_at
            )
            tasks.append(task)
        
        elif recommendation.action_code == "LOCATE_BAG":
            task = self._create_locate_task(
                case_id=case_id,
                recommendation_id=recommendation_id,
                bag_reference=bag_reference,
                deadline_at=case.deadline_at
            )
            tasks.append(task)
        
        elif recommendation.action_code == "MONITOR":
            # No task created for monitoring
            pass
        
        return tasks
    
    def _create_priority_transfer_task(
        self,
        case_id: str,
        recommendation_id: str,
        bag_reference: str,
        deadline_at: datetime
    ) -> Task:
        """Create a priority transfer task assigned to partner."""
        evidence_links = json.dumps([
            "Bag event log",
            "Transfer scan history",
            "Flight departure schedule"
        ])
        
        task = self.task_repo.create(
            case_id=case_id,
            recommendation_id=recommendation_id,
            assigned_role_code="partner",
            assigned_partner_org_code="DNATA",
            bag_reference=bag_reference,
            station_code="DXB",
            flight_context_text="Onward connection to final destination",
            instruction_text="Priority transfer required. Expedite bag to onward flight gate before cutoff.",
            evidence_links_json=evidence_links,
            deadline_at=deadline_at,
            status_code="assigned"
        )
        
        return task
    
    def _create_reschedule_task(
        self,
        case_id: str,
        recommendation_id: str,
        bag_reference: str,
        deadline_at: datetime
    ) -> Task:
        """Create a reschedule connection task assigned to operations."""
        evidence_links = json.dumps([
            "Passenger itinerary",
            "Alternative flight options",
            "Connection analysis"
        ])
        
        task = self.task_repo.create(
            case_id=case_id,
            recommendation_id=recommendation_id,
            assigned_role_code="operations",
            assigned_partner_org_code=None,
            bag_reference=bag_reference,
            station_code="DXB",
            flight_context_text="Missed connection requiring rebooking",
            instruction_text="Reschedule passenger and bag to alternative flight. Update passenger notification.",
            evidence_links_json=evidence_links,
            deadline_at=deadline_at,
            status_code="assigned"
        )
        
        return task
    
    def _create_locate_task(
        self,
        case_id: str,
        recommendation_id: str,
        bag_reference: str,
        deadline_at: datetime
    ) -> Task:
        """Create a locate bag task assigned to partner."""
        evidence_links = json.dumps([
            "Last known location",
            "Transfer scan history",
            "Station baggage hold map"
        ])
        
        task = self.task_repo.create(
            case_id=case_id,
            recommendation_id=recommendation_id,
            assigned_role_code="partner",
            assigned_partner_org_code="DNATA",
            bag_reference=bag_reference,
            station_code="DXB",
            flight_context_text="Bag missing from expected transfer location",
            instruction_text="Locate bag in transfer area or baggage hold. Confirm current location and status.",
            evidence_links_json=evidence_links,
            deadline_at=deadline_at,
            status_code="assigned"
        )
        
        return task
    
    def accept_task_event(
        self,
        task_id: str,
        actor_user_id: str,
        event_type: str,
        note_text: str | None,
        evidence_type: str | None,
        evidence_reference: str | None,
        client_event_id: str
    ) -> tuple[TaskEvidence | None, Task, str]:
        """
        Accept task event submission with status update and case status propagation.
        
        Implements FR-010: task acknowledgement and evidence capture.
        Supports event types: acknowledged, in_progress, completed, evidence_submitted, blocked.
        Updates task status based on event type and propagates to parent case when appropriate.
        Commits evidence and task update atomically with audit event.
        
        Args:
            task_id: Task ID
            actor_user_id: User ID of actor submitting event
            event_type: Event type (acknowledged, in_progress, completed, evidence_submitted, blocked)
            note_text: Optional note text
            evidence_type: Optional evidence type (scan_confirmation, handover_proof, completion_note)
            evidence_reference: Optional evidence reference identifier
            client_event_id: Client-provided idempotency key for replay protection
        
        Returns:
            Tuple of (TaskEvidence or None for idempotent replay, updated Task, case_status)
        
        Raises:
            ValueError: If task not found
        """
        # Verify task exists
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Create evidence with idempotent replay support
        evidence = self.evidence_repo.create(
            task_id=task_id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            note_text=note_text,
            evidence_type=evidence_type,
            evidence_reference=evidence_reference,
            client_event_id=client_event_id
        )
        
        # Update task status based on event type
        new_task_status = task.status_code
        if event_type == "acknowledged":
            new_task_status = "acknowledged"
        elif event_type == "in_progress":
            new_task_status = "in_progress"
        elif event_type == "completed" or event_type == "evidence_submitted":
            new_task_status = "completed"
        elif event_type == "blocked":
            new_task_status = "assigned"  # Reset to assigned for reassignment
        
        # Update task status if changed
        if new_task_status != task.status_code:
            updated = self.task_repo.update_status(task_id, new_task_status)
            if updated:
                task = updated
        
        # Update parent case status when task evidence changes case state
        case = self.case_repo.get_by_id(task.case_id)
        case_status = case.status_code if case else "unknown"
        
        if case and new_task_status == "completed":
            # Check if all tasks for this case are completed
            all_tasks = self.task_repo.list_by_case(task.case_id)
            all_completed = all(t.status_code == "completed" for t in all_tasks)
            
            if all_completed and case.status_code != "closed":
                # Update case status to closed when all tasks completed
                self.case_repo.update_status(task.case_id, "closed")
                case_status = "closed"
            elif case.status_code == "tasked":
                # Update case status to in_recovery when at least one task is in progress or completed
                self.case_repo.update_status(task.case_id, "in_recovery")
                case_status = "in_recovery"
        
        # Commit atomically
        self.db.commit()
        
        return evidence, task, case_status
