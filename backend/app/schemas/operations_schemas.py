"""Operations-facing Pydantic schemas for bag timelines and journey context."""
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class FreshnessStatus(BaseModel):
    """
    Freshness status for a data point.
    Indicates whether information is fresh, stale, or awaiting confirmation.
    """
    state: str  # fresh, stale, or awaiting_confirmation
    age_minutes: Optional[int] = None
    source_system: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class RiskAssessment(BaseModel):
    """
    Connection risk assessment result.
    Separates observed state from predicted risk state.
    """
    risk_label: str  # e.g., "Connection at risk, late inbound", "Transfer scan missing"
    urgency_rank: int  # 1-5, with 1 being most urgent
    observed_state_summary: str  # Confirmed facts from observed events
    predicted_state_summary: str  # Predicted risk and outcome
    time_to_cutoff_minutes: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class BagMilestone(BaseModel):
    """
    Individual bag milestone event.
    Marks observed/derived/estimated status, source system, and freshness.
    """
    event_type: str
    observed_at: datetime
    source_system: str
    fact_type: str  # observed, derived, or estimated
    freshness_state: str  # fresh, stale, or awaiting_confirmation
    location_code: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class JourneyContext(BaseModel):
    """
    Journey context showing inbound/onward flights, connection window,
    and operational changes (gate, stand, aircraft).
    """
    journey_id: str
    inbound_flight: str
    onward_flight: str
    connection_window_minutes: int
    gate_change: Optional[str] = None
    stand_change: Optional[str] = None
    aircraft_change: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class BagTimeline(BaseModel):
    """
    Complete bag timeline with milestones and journey context.
    Used for operations cockpit and case detail views.
    """
    bag_id: str
    bag_tag: str
    passenger_name_masked: str
    journey_context: Optional[JourneyContext]
    milestones: list[BagMilestone]
    
    model_config = ConfigDict(from_attributes=True)


class ExceptionCase(BaseModel):
    """
    Exception case schema for operations views.
    Groups related bags sharing operational recovery context.
    """
    case_id: str
    case_reference: str
    exception_type: str
    severity_code: str = Field(..., serialization_alias="severity")  # critical, high, medium, low
    deadline_at: datetime = Field(..., serialization_alias="deadline_utc")
    status_code: str = Field(..., serialization_alias="status")  # open, under_review, approved, tasked, in_recovery, closed
    observed_state_summary: str
    predicted_state_summary: str
    bag_count: int
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class Recommendation(BaseModel):
    """
    Explainable recovery recommendation schema.
    Each recommendation includes reason, confidence, freshness, and evidence.
    """
    recommendation_id: str
    case_id: str
    action_code: str  # PRIORITY_TRANSFER, RESCHEDULE_CONNECTION, LOCATE_BAG, MONITOR
    action_label: str
    reason_text: str
    confidence_score: float  # 0.00-1.00
    freshness_state: str  # fresh, stale, awaiting_confirmation
    evidence: list[str]  # Evidence summary items
    generated_at: datetime
    superseded_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ApprovalDecisionRequest(BaseModel):
    """
    Request schema for approval or rejection of a recommendation.
    Used by POST /operations/cases/{case_id}/approvals.
    """
    recommendation_id: str
    decision: str  # 'approve' or 'reject'
    rationale: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class TaskSummary(BaseModel):
    """
    Task summary schema for operations and partner views.
    Includes task ID, case ID, status, assigned role, station, deadline, and instruction summary.
    """
    task_id: str
    case_id: str
    status: str  # assigned, acknowledged, in_progress, completed
    assigned_role: str  # operations, partner
    station_code: str
    deadline_utc: datetime
    instruction_summary: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ApprovalDecisionResponse(BaseModel):
    """
    Response schema for approval decision.
    Returns case ID, recommendation ID, decision, decided timestamp, decider, and created tasks.
    """
    case_id: str
    recommendation_id: str
    decision: str  # 'approve' or 'reject'
    decided_at: datetime
    decided_by: str  # Display name of approver
    tasks_created: list[TaskSummary]
    
    model_config = ConfigDict(from_attributes=True)


class AuditEvent(BaseModel):
    """
    Audit event schema for case audit trail.
    Records actor, action, timestamp, entity context, correlation ID, and outcome.
    """
    audit_event_id: str
    actor_user_id: Optional[str] = None  # Nullable for system actions
    action_type: str  # login_success, approval_decision, task_evidence_submitted, etc.
    entity_type: str  # user, exception_case, approval_decision, task, etc.
    entity_id: str
    correlation_id: str
    outcome_code: str  # success, failure, denied, etc.
    detail: dict  # Additional context as JSON
    occurred_at: datetime
    actor_display: Optional[str] = None  # Display name for operations views
    
    model_config = ConfigDict(from_attributes=True)


class CockpitSummary(BaseModel):
    """
    Summary metrics for operations cockpit.
    Shows counts of open cases, urgent cases, impacted bags, and passengers.
    """
    open_cases: int
    urgent_cases: int
    impacted_bags: int
    impacted_passengers: int
    
    model_config = ConfigDict(from_attributes=True)


class CockpitCaseCard(BaseModel):
    """
    Case card for operations cockpit view.
    Condensed case information with priority indicators.
    """
    case_id: str
    severity: str  # critical, high, medium, low
    deadline_utc: datetime
    bag_count: int
    passenger_impact_score: int
    freshness_label: str
    risk_label: str
    primary_reason: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class OperationsCockpitResponse(BaseModel):
    """
    Response schema for GET /operations/cockpit.
    Returns prioritized case overview with summary metrics.
    """
    generated_at: datetime
    freshness_status: str  # fresh, stale, mixed
    summary: CockpitSummary
    cases: list[CockpitCaseCard]
    
    model_config = ConfigDict(from_attributes=True)


class OperationsCaseDetail(BaseModel):
    """
    Detailed case view for operations.
    Includes full case information, bag timelines, recommendations, tasks, and audit trail.
    """
    case: ExceptionCase
    bag_timelines: list[BagTimeline]
    recommendations: list[Recommendation]
    tasks: list[TaskSummary]
    audit_excerpt: list[AuditEvent]
    
    model_config = ConfigDict(from_attributes=True)
