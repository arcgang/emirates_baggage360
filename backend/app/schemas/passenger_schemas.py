"""Passenger-facing Pydantic schemas with passenger-safe filtering."""
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict


class PassengerMilestone(BaseModel):
    """
    Passenger-visible milestone with source system label.
    
    Excludes internal operational details and risk scores.
    """
    milestone_text: str
    source_system: str
    observed_at: datetime
    location_code: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


class PassengerBagStatus(BaseModel):
    """
    Passenger bag status with confirmed milestone and estimated next step.
    
    Implements GET /passenger/bags/{bag_tag}/status response schema per openapi.yaml.
    Provides passenger-safe status composition with explicit uncertainty labeling.
    Excludes internal notes, risk scores, and unauthorized details.
    """
    bag_tag: str
    latest_confirmed_milestone: str
    status_label: str
    estimated_notice: str | None = None
    delayed_case_reference: str | None = None
    next_expected_update: str | None = None
    last_updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PassengerProgressStep(BaseModel):
    """
    Passenger progress step marked as confirmed or estimated.
    
    Implements FR-013: separation of confirmed vs estimated passenger information.
    Each step carries explicit status indicator and optional uncertainty explanation.
    """
    step_text: str
    status: str  # "confirmed" or "estimated"
    timestamp: datetime | None = None
    uncertainty_note: str | None = None
    
    model_config = ConfigDict(from_attributes=True)


class PassengerCaseStatus(BaseModel):
    """
    Passenger delayed-bag case status with progress steps.
    
    Implements GET /passenger/cases/{case_reference} response schema per openapi.yaml.
    Implements FR-013: confirmed vs estimated separation with explicit uncertainty labeling.
    Implements FR-014: delayed-bag case status and next expected update.
    
    Provides passenger-safe case status composition:
    - Latest confirmed status with plain-language description
    - Estimated notice with explicit uncertainty labeling when applicable
    - Progress steps marked as confirmed or estimated
    - Next expected update timestamp
    - Excludes internal operational notes and risk scores
    
    Returns 404 for unauthorized case references to prevent information leakage.
    """
    case_reference: str
    latest_confirmed_status: str
    estimated_notice: str | None = None
    next_expected_update: str
    progress_steps: list[PassengerProgressStep]
    last_updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
