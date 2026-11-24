"""Exception case service for grouping and case management."""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..models.exception_case import ExceptionCase
from ..repositories.bag_repository import BagEventRepository, BagRepository
from ..repositories.exception_case_repository import ExceptionCaseRepository
from ..repositories.journey_repository import JourneyRepository
from ..services.risk_assessment_service import RiskAssessmentService


class ExceptionCaseService:
    """
    Service for exception case grouping and management.
    
    Groups related bags or events into exception cases when they share
    an operational recovery context.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.case_repo = ExceptionCaseRepository(db)
        self.bag_repo = BagRepository(db)
        self.bag_event_repo = BagEventRepository(db)
        self.journey_repo = JourneyRepository(db)
        self.risk_service = RiskAssessmentService(db)
    
    def create_case(
        self,
        bag_ids: list[str],
        exception_type: str,
        created_by_user_id: str
    ) -> ExceptionCase:
        """
        Create an exception case grouping related bags by shared operational recovery context.
        
        Calculates severity based on urgency and passenger impact.
        Sets deadline from onward flight cutoff.
        Generates observed and predicted state summaries.
        
        Args:
            bag_ids: List of bag IDs to group into this case
            exception_type: Type of exception (e.g., "short_connection_risk", "transfer_monitoring")
            created_by_user_id: User ID creating the case
        
        Returns:
            Created ExceptionCase
        """
        if not bag_ids:
            raise ValueError("At least one bag ID is required to create a case")
        
        # Get bag and journey information for severity and deadline calculation
        primary_bag = self.bag_repo.get_by_id(bag_ids[0])
        if not primary_bag:
            raise ValueError(f"Primary bag {bag_ids[0]} not found")
        
        journey = self.journey_repo.get_by_id(primary_bag.journey_id)
        if not journey:
            raise ValueError(f"Journey {primary_bag.journey_id} not found")
        
        journey_legs = self.journey_repo.get_legs_by_journey(primary_bag.journey_id)
        
        # Find onward leg for deadline calculation
        onward_leg = None
        for leg in journey_legs:
            if leg.leg_status == "scheduled":
                onward_leg = leg
                break
        
        # Calculate deadline (use onward flight departure minus safety buffer)
        deadline_at = datetime.now(timezone.utc) + timedelta(hours=2)  # Default 2 hours
        if onward_leg:
            # Set deadline to 90 minutes before departure (cutoff time)
            deadline_at = onward_leg.scheduled_departure_at - timedelta(minutes=90)
        
        # Calculate severity based on time to deadline and risk assessment
        severity_code = self._calculate_severity(bag_ids[0], deadline_at)
        
        # Generate observed state summary from confirmed events
        observed_state_summary = self._generate_observed_state_summary(bag_ids)
        
        # Generate predicted state summary from risk assessment
        predicted_state_summary = self._generate_predicted_state_summary(bag_ids[0], deadline_at)
        
        # Generate case reference
        case_reference = self._generate_case_reference()
        
        # Create case
        case = ExceptionCase(
            id=str(uuid.uuid4()),
            case_reference=case_reference,
            exception_type=exception_type,
            severity_code=severity_code,
            deadline_at=deadline_at,
            status_code="open",
            observed_state_summary=observed_state_summary,
            predicted_state_summary=predicted_state_summary,
            created_by_user_id=created_by_user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        case = self.case_repo.create(case)
        
        # Add bags to case
        for idx, bag_id in enumerate(bag_ids):
            self.case_repo.add_bag_to_case(
                case_id=case.id,
                bag_id=bag_id,
                primary_flag=(idx == 0)  # First bag is primary
            )
        
        return case
    
    def _calculate_severity(self, bag_id: str, deadline_at: datetime) -> str:
        """
        Calculate severity based on urgency and passenger impact.
        
        Severity levels:
        - critical: < 60 minutes to deadline
        - high: 60-90 minutes to deadline
        - medium: 90-180 minutes to deadline
        - low: > 180 minutes to deadline
        """
        time_to_deadline = deadline_at - datetime.now(timezone.utc)
        minutes_to_deadline = int(time_to_deadline.total_seconds() / 60)
        
        # Get risk assessment for additional context
        bag = self.bag_repo.get_by_id(bag_id)
        if not bag:
            # If no bag found, default to high severity
            if minutes_to_deadline < 60:
                return "critical"
            else:
                return "high"
        
        # For now, simplified risk assessment without full case object
        # In full implementation, would call risk_service.calculate_connection_risk
        risk_urgency = 3  # Default medium urgency
        
        # Critical if urgent
        if minutes_to_deadline < 60:
            return "critical"
        elif minutes_to_deadline < 90 or risk_urgency <= 2:
            return "high"
        elif minutes_to_deadline < 180:
            return "medium"
        else:
            return "low"
    
    def _generate_observed_state_summary(self, bag_ids: list[str]) -> str:
        """
        Generate observed state summary from confirmed events.
        
        Returns a text summary of confirmed facts from bag events.
        """
        summaries = []
        
        for bag_id in bag_ids:
            bag = self.bag_repo.get_by_id(bag_id)
            if not bag:
                continue
            
            events = self.bag_event_repo.get_by_bag(bag_id)
            if not events:
                summaries.append(f"Bag {bag.bag_tag}: no events recorded")
                continue
            
            # Get latest observed event
            latest_observed = None
            for event in reversed(events):
                if event.fact_type == "observed":
                    latest_observed = event
                    break
            
            if latest_observed:
                age_minutes = int((datetime.now(timezone.utc) - latest_observed.observed_at).total_seconds() / 60)
                summaries.append(
                    f"Bag {bag.bag_tag}: {latest_observed.event_type} at {latest_observed.event_station}, "
                    f"{age_minutes} minutes ago"
                )
            else:
                summaries.append(f"Bag {bag.bag_tag}: no observed events")
        
        return "; ".join(summaries)
    
    def _generate_predicted_state_summary(self, bag_id: str, deadline_at: datetime) -> str:
        """
        Generate predicted state summary from risk assessment.
        
        Returns a text summary of risk assessment and predicted outcomes.
        """
        time_to_deadline = deadline_at - datetime.now(timezone.utc)
        minutes_to_deadline = int(time_to_deadline.total_seconds() / 60)
        
        # Generate risk label based on time
        if minutes_to_deadline < 60:
            risk_label = "Critical: transfer scan missing, approaching cutoff"
        elif minutes_to_deadline < 90:
            risk_label = "Connection at risk, late inbound"
        elif minutes_to_deadline < 180:
            risk_label = "Moderate: sufficient buffer"
        else:
            risk_label = "Normal: on track"
        
        return f"{risk_label}, {minutes_to_deadline} minutes to deadline"
    
    def _generate_case_reference(self) -> str:
        """Generate a unique case reference code."""
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        # In a real system, would use a sequence or atomic counter
        # For demo, use timestamp-based suffix
        suffix = datetime.now(timezone.utc).strftime("%H%M%S")
        return f"BC-DXB-{today}-{suffix}"
    
    def get_case_by_id(self, case_id: str) -> ExceptionCase | None:
        """Get exception case by ID."""
        return self.case_repo.get_by_id(case_id)
    
    def get_case_by_reference(self, case_reference: str) -> ExceptionCase | None:
        """Get exception case by reference."""
        return self.case_repo.get_by_reference(case_reference)
    
    def list_prioritized_cases(
        self,
        severity: str | None = None,
        station_scope: str | None = None,
        status_code: str | None = "open"
    ) -> list[ExceptionCase]:
        """
        List exception cases with prioritization by urgency, deadline, and severity.
        
        Args:
            severity: Filter by severity (critical, high, medium, low)
            station_scope: Filter by station (not implemented in demo - would use case metadata)
            status_code: Filter by status (default: open)
        
        Returns:
            List of ExceptionCase ordered by deadline ascending (most urgent first)
        """
        return self.case_repo.list_prioritized(
            severity=severity,
            station_scope=station_scope,
            status_code=status_code,
            order_by_deadline=True
        )
    
    def update_case_status(self, case_id: str, new_status: str) -> ExceptionCase | None:
        """Update case status."""
        return self.case_repo.update_status(case_id, new_status)
