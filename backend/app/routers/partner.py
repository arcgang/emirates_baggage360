"""Partner router for role-scoped partner task queue and task detail."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.partner_schemas import (
    PartnerTaskCard,
    PartnerTaskQueueResponse,
    PartnerTaskDetail,
    TaskEventRequest,
    TaskEventResponse,
)
from ..repositories.task_repository import TaskRepository
from ..repositories.task_evidence_repository import TaskEvidenceRepository
from ..services.task_dispatch_service import TaskDispatchService
from ..models.user import User

router = APIRouter()


def format_task_reference(task_id: str, station_code: str) -> str:
    """Format task ID as TSK-{STATION}-{last 4 digits of UUID as int}."""
    # Extract last segment of UUID and convert to integer
    try:
        uuid_last_segment = task_id.split('-')[-1]
        task_number = int(uuid_last_segment, 16)  # Convert hex to decimal
        return f"TSK-{station_code}-{task_number}"
    except (ValueError, IndexError):
        # Fallback to showing last 8 characters
        return f"TSK-{station_code}-{task_id[-8:]}"


def get_current_partner_user(db: Session = Depends(get_db)) -> User:
    """Get current authenticated partner user.
    
    For this initial implementation, returns the seed partner user.
    Full authentication will be implemented in subsequent tasks.
    """
    # For demo, return seed partner user ahmed.hassan@dnata.ae
    user = db.query(User).filter(User.external_subject == "ahmed.hassan@dnata.ae").first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    if user.role_code != "partner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FORBIDDEN_SCOPE"
        )
    return user


@router.get("/partner/tasks", response_model=PartnerTaskQueueResponse)
def get_partner_tasks(
    status: str = Query(None, pattern="^(assigned|acknowledged|in_progress|completed)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_partner_user)
):
    """
    Get role-scoped partner work queue.
    
    Returns tasks assigned to the current partner user's organization,
    filtered by optional status parameter.
    """
    repo = TaskRepository(db)
    tasks = repo.list_by_partner_org_and_role(
        partner_org_code=current_user.partner_org_code,
        assigned_role_code="partner",
        status_code=status
    )
    
    # Build PartnerTaskCard for each task
    task_cards = [
        PartnerTaskCard(
            task_id=format_task_reference(str(task.id), task.station_code),
            case_id=str(task.case_id),
            bag_reference=task.bag_reference,
            flight_context=task.flight_context_text,
            station_code=task.station_code,
            deadline_utc=task.deadline_at,
            status=task.status_code,
            instruction_summary=task.instruction_text[:100] + "..." if len(task.instruction_text) > 100 else task.instruction_text
        )
        for task in tasks
    ]
    
    return PartnerTaskQueueResponse(
        items=task_cards,
        total=len(task_cards),
        generated_at=datetime.now(timezone.utc)
    )


@router.get("/partner/tasks/{task_id}", response_model=PartnerTaskDetail)
def get_partner_task_detail(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_partner_user)
):
    """
    Get partner task detail with masked passenger data and limited case context.
    
    Returns 403 FORBIDDEN_SCOPE if task is not assigned to current user's organization.
    
    task_id can be either the full UUID or the formatted reference (TSK-DXB-1187).
    """
    # If task_id is a formatted reference, extract the UUID
    actual_task_id = task_id
    if task_id.startswith("TSK-"):
        # Extract number from TSK-{STATION}-{NUMBER}
        try:
            parts = task_id.split("-")
            if len(parts) == 3:
                task_number = int(parts[2])
                # Convert back to UUID format: last segment is hex of this number
                hex_segment = format(task_number, '012x')  # 12 hex digits
                actual_task_id = f"00000000-0000-0000-0000-{hex_segment}"
        except (ValueError, IndexError):
            # Keep original task_id if parsing fails
            pass
    
    repo = TaskRepository(db)
    task = repo.get_by_id_with_partner_scope(actual_task_id, current_user.partner_org_code)
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FORBIDDEN_SCOPE"
        )
    
    # Build PartnerTaskDetail
    # Parse evidence_links_json if present
    evidence_links = []
    if task.evidence_links_json:
        import json
        try:
            evidence_links = json.loads(task.evidence_links_json)
        except (json.JSONDecodeError, TypeError):
            evidence_links = []
    
    # Parse instructions - split by newline or treat as single instruction
    instructions = [line.strip() for line in task.instruction_text.split("\n") if line.strip()]
    if not instructions:
        instructions = [task.instruction_text]
    
    # Get observed state summary from case if available
    observed_state_summary = None
    passenger_name_masked = "P***"  # Default masked value
    if task.case:
        observed_state_summary = task.case.observed_state_summary
        # Mask passenger reference - get from first bag in case via case_bags relationship
        if task.case.case_bags and len(task.case.case_bags) > 0:
            first_case_bag = task.case.case_bags[0]
            # Load the bag to get journey and passenger details
            from ..models.bag import Bag
            bag = db.query(Bag).filter(Bag.id == first_case_bag.bag_id).first()
            if bag and bag.journey and bag.journey.passenger_reference:
                # Mask passenger reference: show first 3 chars + asterisks (same as operations.py)
                passenger_ref = bag.journey.passenger_reference
                if len(passenger_ref) > 3:
                    passenger_name_masked = passenger_ref[:3] + "***"
                else:
                    passenger_name_masked = "***"
    
    return PartnerTaskDetail(
        task_id=format_task_reference(str(task.id), task.station_code),
        case_id=str(task.case_id),
        case_reference=task.case.case_reference if task.case else None,
        bag_reference=task.bag_reference,
        flight_context=task.flight_context_text,
        station_code=task.station_code,
        deadline_utc=task.deadline_at,
        status=task.status_code,
        instructions=instructions,
        evidence_links=evidence_links,
        observed_state_summary=observed_state_summary,
        passenger_name_masked=passenger_name_masked
    )


@router.post("/partner/tasks/{task_id}/events", response_model=TaskEventResponse)
def post_partner_task_event(
    task_id: str,
    request: TaskEventRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_partner_user)
):
    """
    Submit acknowledgement or evidence for a partner task.
    
    Accepts event types: acknowledged, in_progress, completed.
    Returns 403 FORBIDDEN_SCOPE if task is not assigned to current user's organization.
    
    task_id can be either the full UUID or the formatted reference (TSK-DXB-1187).
    """
    # If task_id is a formatted reference, extract the UUID
    actual_task_id = task_id
    if task_id.startswith("TSK-"):
        # Extract number from TSK-{STATION}-{NUMBER}
        try:
            parts = task_id.split("-")
            if len(parts) == 3:
                task_number = int(parts[2])
                # Convert back to UUID format: last segment is hex of this number
                hex_segment = format(task_number, '012x')  # 12 hex digits
                actual_task_id = f"00000000-0000-0000-0000-{hex_segment}"
        except (ValueError, IndexError):
            # Keep original task_id if parsing fails
            pass
    
    # Verify task belongs to current user's organization
    repo = TaskRepository(db)
    task = repo.get_by_id_with_partner_scope(actual_task_id, current_user.partner_org_code)
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FORBIDDEN_SCOPE"
        )
    
    # Submit task event
    task_dispatch_service = TaskDispatchService(db)
    try:
        evidence, updated_task, case_status = task_dispatch_service.accept_task_event(
            task_id=actual_task_id,
            actor_user_id=str(current_user.id),
            event_type=request.event_type,
            note_text=request.note,
            evidence_type=request.evidence_type,
            evidence_reference=request.evidence_reference,
            client_event_id=request.client_event_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return TaskEventResponse(
        task_id=format_task_reference(str(updated_task.id), updated_task.station_code),
        event_type=request.event_type,
        recorded_at=datetime.now(timezone.utc),
        case_status=case_status
    )
