"""Risk assessment service for connection risk evaluation and urgency ranking."""
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..models.bag import Bag, BagEvent
from ..models.exception_case import ExceptionCase
from ..models.journey import JourneyLeg
from ..repositories.bag_repository import BagEventRepository
from ..repositories.journey_repository import JourneyRepository


class RiskAssessmentService:
    """
    Service for evaluating connection risk and urgency ranking.
    
    Computes risk labels based on bag event state, onward connection context,
    time to cutoff, and passenger impact indicators. Maintains separation between
    observed state and predicted risk state.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.bag_event_repo = BagEventRepository(db)
        self.journey_repo = JourneyRepository(db)
    
    def calculate_connection_risk(
        self, 
        bag: Bag, 
        case: ExceptionCase,
        latest_event: BagEvent | None = None
    ) -> dict:
        """
        Calculate connection risk for a bag and case.
        
        Uses bag event state, onward connection context, time to cutoff,
        and passenger impact to determine risk label and urgency rank.
        
        Args:
            bag: Bag model instance
            case: ExceptionCase model instance
            latest_event: Optional latest BagEvent (fetched if not provided)
        
        Returns:
            Dict with risk_label, urgency_rank, observed_state_summary,
            predicted_state_summary, time_to_cutoff_minutes
        """
        # Get latest event if not provided
        if latest_event is None:
            events = self.bag_event_repo.get_by_bag(bag.id)
            latest_event = events[-1] if events else None
        
        # Get journey context
        journey_legs = self.journey_repo.get_legs_by_journey(bag.journey_id)
        inbound_leg = None
        onward_leg = None
        
        for leg in journey_legs:
            if leg.leg_status == "arrived":
                inbound_leg = leg
            elif leg.leg_status == "scheduled":
                onward_leg = leg
                break
        
        # Calculate time to cutoff
        now = datetime.now(timezone.utc)
        time_to_cutoff_minutes = None
        if onward_leg and onward_leg.scheduled_departure_at:
            # Assume 90 minutes before departure is the cutoff
            cutoff_time = onward_leg.scheduled_departure_at - timedelta(minutes=90)
            time_to_cutoff = cutoff_time - now
            time_to_cutoff_minutes = int(time_to_cutoff.total_seconds() / 60)
        
        # Determine risk label based on event state and time to cutoff
        risk_label = self._evaluate_risk_label(
            latest_event, 
            time_to_cutoff_minutes,
            inbound_leg,
            onward_leg
        )
        
        # Calculate urgency rank (1-5, with 1 being most urgent)
        urgency_rank = self._calculate_urgency_rank(
            risk_label,
            time_to_cutoff_minutes,
            case.severity_code
        )
        
        # Build observed vs predicted state summary
        observed_state = self._build_observed_state_summary(latest_event, inbound_leg)
        predicted_state = self._build_predicted_state_summary(
            risk_label,
            time_to_cutoff_minutes,
            onward_leg
        )
        
        return {
            "risk_label": risk_label,
            "urgency_rank": urgency_rank,
            "observed_state_summary": observed_state,
            "predicted_state_summary": predicted_state,
            "time_to_cutoff_minutes": time_to_cutoff_minutes,
        }
    
    def evaluate_risk(
        self,
        bag_id: str,
        case_id: str
    ) -> dict:
        """
        Evaluate risk for a bag within a case context.
        
        Returns risk_label, urgency_rank, observed vs predicted state summary.
        """
        # Fetch bag and case
        bag = self.db.get(Bag, bag_id)
        case = self.db.get(ExceptionCase, case_id)
        
        if not bag or not case:
            raise ValueError("Bag or case not found")
        
        return self.calculate_connection_risk(bag, case)
    
    def _evaluate_risk_label(
        self,
        latest_event: BagEvent | None,
        time_to_cutoff_minutes: int | None,
        inbound_leg: JourneyLeg | None,
        onward_leg: JourneyLeg | None
    ) -> str:
        """
        Evaluate risk label based on event state and connection context.
        
        Returns labels such as:
        - "Connection at risk, late inbound"
        - "Transfer scan missing"
        - "Critical: approaching cutoff"
        - "Moderate: sufficient buffer"
        """
        # No latest event means we have no visibility
        if not latest_event:
            return "Transfer scan missing"
        
        # Check if transfer scan is missing (derived/estimated only, no observed transfer)
        if latest_event.fact_type in ["derived", "estimated"] and latest_event.event_type in ["transfer_pending", "awaiting_scan"]:
            if time_to_cutoff_minutes is not None and time_to_cutoff_minutes < 60:
                return "Critical: transfer scan missing, approaching cutoff"
            return "Transfer scan missing"
        
        # Check time to cutoff
        if time_to_cutoff_minutes is not None:
            if time_to_cutoff_minutes < 45:
                return "Critical: approaching cutoff"
            elif time_to_cutoff_minutes < 90:
                return "Connection at risk, late inbound"
            else:
                return "Moderate: sufficient buffer"
        
        # Check if inbound is late
        if inbound_leg and inbound_leg.actual_arrival_at and inbound_leg.scheduled_arrival_at:
            delay = (inbound_leg.actual_arrival_at - inbound_leg.scheduled_arrival_at).total_seconds() / 60
            if delay > 30:
                return "Connection at risk, late inbound"
        
        return "Normal: on track"
    
    def _calculate_urgency_rank(
        self,
        risk_label: str,
        time_to_cutoff_minutes: int | None,
        severity_code: str
    ) -> int:
        """
        Calculate urgency rank (1-5, with 1 being most urgent).
        
        Based on risk label, time to cutoff, and case severity.
        """
        # Base urgency from risk label
        if "Critical" in risk_label:
            base_urgency = 1
        elif "Connection at risk" in risk_label:
            base_urgency = 2
        elif "Transfer scan missing" in risk_label:
            base_urgency = 3
        elif "Moderate" in risk_label:
            base_urgency = 4
        else:
            base_urgency = 5
        
        # Adjust based on time to cutoff
        if time_to_cutoff_minutes is not None:
            if time_to_cutoff_minutes < 30:
                base_urgency = min(base_urgency, 1)
            elif time_to_cutoff_minutes < 60:
                base_urgency = min(base_urgency, 2)
        
        # Adjust based on severity
        if severity_code == "critical":
            base_urgency = min(base_urgency, 1)
        elif severity_code == "high":
            base_urgency = min(base_urgency, 2)
        
        return base_urgency
    
    def _build_observed_state_summary(
        self,
        latest_event: BagEvent | None,
        inbound_leg: JourneyLeg | None
    ) -> str:
        """Build observed state summary from confirmed events."""
        if not latest_event:
            return "No bag events observed"
        
        parts = []
        
        # Last confirmed event
        if latest_event.fact_type == "observed":
            parts.append(f"Last confirmed: {latest_event.event_type} at {latest_event.event_station}")
        else:
            parts.append(f"Last event: {latest_event.event_type} (derived/estimated)")
        
        # Inbound status
        if inbound_leg and inbound_leg.actual_arrival_at and inbound_leg.scheduled_arrival_at:
            delay = (inbound_leg.actual_arrival_at - inbound_leg.scheduled_arrival_at).total_seconds() / 60
            if delay > 15:
                parts.append(f"Inbound delayed by {int(delay)} minutes")
            else:
                parts.append("Inbound arrived on time")
        
        return "; ".join(parts)
    
    def _build_predicted_state_summary(
        self,
        risk_label: str,
        time_to_cutoff_minutes: int | None,
        onward_leg: JourneyLeg | None
    ) -> str:
        """Build predicted state summary based on risk assessment."""
        parts = [f"Risk: {risk_label}"]
        
        if time_to_cutoff_minutes is not None:
            if time_to_cutoff_minutes > 0:
                parts.append(f"{time_to_cutoff_minutes} minutes to cutoff")
            else:
                parts.append("Cutoff passed")
        
        if onward_leg:
            parts.append(f"Target: {onward_leg.flight_number} to {onward_leg.arrival_station}")
        
        return "; ".join(parts)
