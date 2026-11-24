"""Operations router for case management and approvals."""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..models.exception_case import ExceptionCase as ExceptionCaseModel
from ..repositories.audit_repository import AuditRepository
from ..repositories.bag_repository import BagEventRepository, BagRepository
from ..repositories.exception_case_repository import ExceptionCaseRepository
from ..repositories.journey_repository import JourneyRepository
from ..repositories.recommendation_repository import RecommendationRepository
from ..repositories.task_repository import TaskRepository
from ..schemas.operations_schemas import (
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    AuditEvent,
    BagMilestone,
    BagTimeline,
    CockpitCaseCard,
    CockpitSummary,
    ExceptionCase,
    JourneyContext,
    OperationsCaseDetail,
    OperationsCockpitResponse,
    Recommendation,
    TaskSummary,
)
from ..services.approval_service import ApprovalService
from ..services.exception_case_service import ExceptionCaseService
from ..services.task_dispatch_service import TaskDispatchService

router = APIRouter()


@router.get("/operations/cockpit", response_model=OperationsCockpitResponse)
def get_operations_cockpit(
    bank_window: str = "current",
    station: str = "DXB",
    db: Session = Depends(get_db)
):
    """
    Get prioritized operational cockpit cases.
    
    Returns open cases ordered by urgency, with summary metrics.
    
    Args:
        bank_window: Time window filter (current, next_2h, custom) - not fully implemented in demo
        station: Station code filter (default: DXB) - not fully implemented in demo
        db: Database session
    
    Returns:
        OperationsCockpitResponse with summary and prioritized case cards
    """
    # Get open cases via ExceptionCaseService
    case_service = ExceptionCaseService(db)
    open_cases = case_service.list_prioritized_cases(status_code="open")
    
    # Calculate summary metrics
    total_open_cases = len(open_cases)
    urgent_cases_count = sum(
        1 for case in open_cases 
        if case.severity_code in ["critical", "high"]
    )
    
    # Get bag count from case_bags relationship
    case_repo = ExceptionCaseRepository(db)
    total_bags = sum(case_repo.get_case_bag_count(case.id) for case in open_cases)
    
    # Estimate passenger impact (1 passenger per bag for demo simplification)
    estimated_passengers = total_bags
    
    # Determine overall freshness status
    freshness_status = "fresh"  # Simplified - would check event ages in full implementation
    
    # Build case cards
    case_cards = []
    for case in open_cases:
        bag_count = case_repo.get_case_bag_count(case.id)
        
        # Calculate passenger impact score (simplified: bag_count * severity weight)
        severity_weights = {"critical": 100, "high": 50, "medium": 25, "low": 10}
        impact_score = bag_count * severity_weights.get(case.severity_code, 10)
        
        # Determine freshness label (simplified)
        freshness_label = "fresh"
        
        case_cards.append(CockpitCaseCard(
            case_id=case.id,
            severity=case.severity_code,
            deadline_utc=case.deadline_at,
            bag_count=bag_count,
            passenger_impact_score=impact_score,
            freshness_label=freshness_label,
            risk_label=case.predicted_state_summary,
            primary_reason=case.exception_type
        ))
    
    summary = CockpitSummary(
        open_cases=total_open_cases,
        urgent_cases=urgent_cases_count,
        impacted_bags=total_bags,
        impacted_passengers=estimated_passengers
    )
    
    return OperationsCockpitResponse(
        generated_at=datetime.now(timezone.utc),
        freshness_status=freshness_status,
        summary=summary,
        cases=case_cards
    )


@router.get("/operations/cases/{case_id}", response_model=OperationsCaseDetail)
def get_operations_case_detail(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Get operational case detail.
    
    Returns full case information including bag timelines, recommendations, tasks, and audit trail.
    
    Args:
        case_id: Exception case ID (UUID) or case reference (e.g., BC-DXB-240611)
        db: Database session
    
    Returns:
        OperationsCaseDetail with complete case information
    
    Raises:
        404: Case not found
    """
    # Get case - support both UUID and case reference
    case_service = ExceptionCaseService(db)
    if case_id.startswith('BC-'):
        # Case reference format - look up by case_reference
        case = db.query(ExceptionCaseModel).filter(ExceptionCaseModel.case_reference == case_id).first()
    else:
        # UUID format
        case = case_service.get_case_by_id(case_id)
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found"
        )
    
    # Get bags for this case
    case_repo = ExceptionCaseRepository(db)
    case_bags = case_repo.get_bags_by_case(str(case.id))
    
    # Build bag timelines
    bag_repo = BagRepository(db)
    bag_event_repo = BagEventRepository(db)
    
    bag_timelines = []
    for case_bag in case_bags:
        bag = bag_repo.get_by_id(case_bag.bag_id)
        if not bag:
            continue
        
        # Get events for bag
        events = bag_event_repo.get_by_bag(bag.id)
        
        # Convert to milestones
        milestones = []
        for event in events:
            milestones.append(BagMilestone(
                event_type=event.event_type,
                observed_at=event.observed_at,
                source_system=event.source_system,
                fact_type=event.fact_type,
                freshness_state=bag_event_repo.calculate_freshness_state(event),
                location_code=event.event_station
            ))
        
        # Get journey context
        journey_context = None
        if bag.journey_id:
            journey_repo = JourneyRepository(db)
            journey = journey_repo.get_by_id(bag.journey_id)
            if journey:
                legs = journey_repo.get_legs_by_journey(bag.journey_id)
                
                # Find inbound and onward legs
                inbound_flight = "Unknown"
                onward_flight = "Unknown"
                connection_window_minutes = 0
                
                if len(legs) >= 2:
                    inbound_leg = legs[0]
                    onward_leg = legs[1]
                    inbound_flight = inbound_leg.flight_number
                    onward_flight = onward_leg.flight_number
                    
                    # Calculate connection window
                    if inbound_leg.scheduled_arrival_at and onward_leg.scheduled_departure_at:
                        delta = onward_leg.scheduled_departure_at - inbound_leg.scheduled_arrival_at
                        connection_window_minutes = int(delta.total_seconds() / 60)
                
                journey_context = JourneyContext(
                    journey_id=bag.journey_id,
                    inbound_flight=inbound_flight,
                    onward_flight=onward_flight,
                    connection_window_minutes=connection_window_minutes,
                    gate_change=None,  # Would extract from journey metadata in full implementation
                    stand_change=None,
                    aircraft_change=None
                )
        
        # Mask passenger reference (take first 3 chars + asterisks)
        passenger_ref = bag.journey.passenger_reference if bag.journey else None
        masked_name = passenger_ref[:3] + "***" if passenger_ref and len(passenger_ref) > 3 else "***"
        
        bag_timelines.append(BagTimeline(
            bag_id=bag.id,
            bag_tag=bag.bag_tag,
            passenger_name_masked=masked_name,
            journey_context=journey_context,
            milestones=milestones
        ))
    
    # Get recommendations
    rec_repo = RecommendationRepository(db)
    db_recommendations = rec_repo.get_by_case(str(case_id), include_superseded=False)
    
    recommendations = []
    for rec in db_recommendations:
        recommendations.append(Recommendation(
            recommendation_id=rec.id,
            case_id=rec.case_id,
            action_code=rec.action_code,
            action_label=rec.action_label,
            reason_text=rec.reason_text,
            confidence_score=rec.confidence_score,
            freshness_state=rec.freshness_state,
            evidence=rec.evidence_json.split(",") if rec.evidence_json else [],
            generated_at=rec.generated_at,
            superseded_at=rec.superseded_at
        ))
    
    # Get tasks
    task_repo = TaskRepository(db)
    db_tasks = task_repo.list_by_case(str(case_id))
    
    tasks = []
    for task in db_tasks:
        tasks.append(TaskSummary(
            task_id=task.id,
            case_id=task.case_id,
            status=task.status_code,
            assigned_role=task.assigned_role_code,
            station_code=task.station_code,
            deadline_utc=task.deadline_at,
            instruction_summary=task.instruction_text[:100] if task.instruction_text else None
        ))
    
    # Get audit events (last 20 events for this case)
    audit_repo = AuditRepository(db)
    db_audit_events = audit_repo.get_events_by_entity("exception_case", str(case_id), limit=20)
    
    audit_excerpt = []
    for audit_event in db_audit_events:
        # Get actor display name if available
        actor_display = "System"
        if audit_event.actor_user_id:
            actor = db.query(User).filter(User.id == audit_event.actor_user_id).first()
            actor_display = actor.display_name if actor else "Unknown User"
        
        audit_excerpt.append(AuditEvent(
            audit_event_id=audit_event.id,
            actor_user_id=audit_event.actor_user_id,
            action_type=audit_event.action_type,
            entity_type=audit_event.entity_type,
            entity_id=audit_event.entity_id,
            correlation_id=audit_event.correlation_id,
            outcome_code=audit_event.outcome_code,
            detail={},  # Simplified - would parse detail_json in full implementation
            occurred_at=audit_event.occurred_at,
            actor_display=actor_display
        ))
    
    # Build response
    return OperationsCaseDetail(
        case=ExceptionCase(
            case_id=case.id,
            case_reference=case.case_reference,
            exception_type=case.exception_type,
            severity_code=case.severity_code,
            deadline_at=case.deadline_at,
            status_code=case.status_code,
            observed_state_summary=case.observed_state_summary,
            predicted_state_summary=case.predicted_state_summary,
            bag_count=len(case_bags),
            created_at=case.created_at,
            updated_at=case.updated_at,
            closed_at=case.closed_at
        ),
        bag_timelines=bag_timelines,
        recommendations=recommendations,
        tasks=tasks,
        audit_excerpt=audit_excerpt
    )


@router.post("/operations/cases/{case_id}/approvals", response_model=ApprovalDecisionResponse)
def post_case_approval(
    case_id: str,
    request: ApprovalDecisionRequest,
    db: Session = Depends(get_db)
):
    """
    Approve or reject a recommendation for a case.
    
    This endpoint enforces FR-007: human approval is mandatory before task dispatch.
    
    - Validates case and recommendation exist
    - Records approval decision with approver identity, timestamp, decision code, rationale
    - If approved, generates operational tasks via TaskDispatchService
    - If rejected, no tasks created
    - Returns approval decision with list of created tasks
    
    Args:
        case_id: Exception case ID
        request: Approval decision request with recommendation_id, decision, rationale
        db: Database session
    
    Returns:
        ApprovalDecisionResponse with decision details and created tasks
    
    Raises:
        400: Invalid decision code
        404: Case or recommendation not found
        409: Recommendation must be approved before dispatch (from task creation)
    """
    # For this scaffold, use a stub user ID (operations user from seed)
    # Production implementation will extract user from JWT token
    decided_by_user_id = "00000000-0000-0000-0000-000000000001"
    
    # Resolve case_id if it's a case reference
    actual_case_id = case_id
    if case_id.startswith('BC-'):
        # Case reference format - look up UUID
        case = db.query(ExceptionCaseModel).filter(ExceptionCaseModel.case_reference == case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )
        actual_case_id = str(case.id)
    
    # Normalize decision code
    decision_code = "approved" if request.decision == "approve" else "rejected"
    
    try:
        # Record approval decision
        approval_service = ApprovalService(db)
        approval = approval_service.record_approval_decision(
            case_id=actual_case_id,
            recommendation_id=request.recommendation_id,
            decided_by_user_id=decided_by_user_id,
            decision_code=decision_code,
            rationale_text=request.rationale
        )
        
        # Create tasks if approved
        tasks = []
        if decision_code == "approved":
            task_dispatch_service = TaskDispatchService(db)
            created_tasks = task_dispatch_service.create_tasks_for_approved_recommendation(
                case_id=actual_case_id,
                recommendation_id=request.recommendation_id
            )
            
            # Convert to TaskSummary schemas
            for task in created_tasks:
                tasks.append(TaskSummary(
                    task_id=task.id,
                    case_id=task.case_id,
                    status=task.status_code,
                    assigned_role=task.assigned_role_code,
                    station_code=task.station_code,
                    deadline_utc=task.deadline_at,
                    instruction_summary=task.instruction_text[:100] if task.instruction_text else None
                ))
        
        # Get decider display name
        decider = db.query(User).filter(User.id == decided_by_user_id).first()
        decided_by_name = decider.display_name if decider else "Unknown"
        
        return ApprovalDecisionResponse(
            case_id=case_id,
            recommendation_id=request.recommendation_id,
            decision=request.decision,
            decided_at=approval.decided_at,
            decided_by=decided_by_name,
            tasks_created=tasks
        )
    
    except ValueError as e:
        # Case or recommendation not found, or invalid decision code
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except PermissionError as e:
        # Recommendation not approved (409 conflict)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
