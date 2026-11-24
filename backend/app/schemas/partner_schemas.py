"""Partner-facing Pydantic schemas with least-privilege filtering."""
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict


class PartnerTaskCard(BaseModel):
    """
    Partner task card for work queue display.
    
    Excludes internal notes, risk scores, and unrelated passenger data per FR-009.
    Passenger names are masked for privacy.
    """
    task_id: str
    case_id: str
    bag_reference: str
    flight_context: str
    station_code: str
    deadline_utc: datetime
    status: str  # assigned, acknowledged, in_progress, completed
    instruction_summary: str
    
    model_config = ConfigDict(from_attributes=True)


class PartnerTaskQueueResponse(BaseModel):
    """
    Partner task queue response with role-scoped tasks.
    
    Implements GET /partner/tasks response schema per openapi.yaml.
    Returns tasks filtered by partner organization and role.
    """
    items: list[PartnerTaskCard]
    total: int
    generated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PartnerTaskDetail(BaseModel):
    """
    Partner task detail with masked passenger data and limited case context.
    
    Implements GET /partner/tasks/{task_id} response schema per openapi.yaml.
    Excludes internal operational notes, risk scores, and unrelated passenger details.
    """
    task_id: str
    case_id: str
    case_reference: str
    bag_reference: str
    flight_context: str
    station_code: str
    deadline_utc: datetime
    status: str
    instructions: list[str]
    evidence_links: list[str]
    
    # Limited case context (no internal notes, no risk scores)
    observed_state_summary: str | None = None
    passenger_name_masked: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


class TaskEventRequest(BaseModel):
    """
    Partner task event submission request.
    
    Implements POST /partner/tasks/{task_id}/events request schema per openapi.yaml.
    Supports acknowledgement, in_progress, and completed event types with optional evidence.
    """
    event_type: str  # acknowledged, in_progress, completed
    client_event_id: str
    note: str | None = None
    evidence_type: str | None = None  # scan_confirmation, handover_proof, completion_note
    evidence_reference: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


class TaskEventResponse(BaseModel):
    """
    Partner task event submission response.
    
    Implements POST /partner/tasks/{task_id}/events response schema per openapi.yaml.
    Returns task event confirmation with updated case status.
    """
    task_id: str
    event_type: str
    recorded_at: datetime
    case_status: str
    
    model_config = ConfigDict(from_attributes=True)
