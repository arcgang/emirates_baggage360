"""Recommendation service for generating explainable recovery recommendations."""
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from ..models.recommendation import Recommendation
from ..repositories.bag_repository import BagEventRepository, BagRepository
from ..repositories.exception_case_repository import ExceptionCaseRepository
from ..repositories.journey_repository import JourneyRepository
from ..repositories.recommendation_repository import RecommendationRepository


class RecommendationService:
    """
    Service for generating explainable recovery recommendations.
    
    Each recommendation includes action code, label, reason explaining why,
    confidence score (0.00-1.00), freshness state, and evidence JSON
    with supporting bag events and journey context.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.rec_repo = RecommendationRepository(db)
        self.case_repo = ExceptionCaseRepository(db)
        self.bag_repo = BagRepository(db)
        self.bag_event_repo = BagEventRepository(db)
        self.journey_repo = JourneyRepository(db)
    
    def generate_recommendations(self, case_id: str) -> list[Recommendation]:
        """
        Generate recommendations for an exception case with explainability.
        
        Recommendation action codes include:
        - PRIORITY_TRANSFER: Expedite transfer to connection
        - RESCHEDULE_CONNECTION: Move to alternative flight
        - LOCATE_BAG: Search for missing bag
        - MONITOR: Continue monitoring without intervention
        
        Each recommendation includes:
        - action_label: Human-readable action description
        - reason_text: Explanation of why this action is recommended
        - confidence_score: 0.00-1.00 confidence in this recommendation
        - freshness_state: fresh/stale/awaiting_confirmation based on data age
        - evidence_json: Supporting bag events and journey context
        
        Args:
            case_id: Exception case ID
        
        Returns:
            List of Recommendation objects ordered by confidence descending
        """
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        # Get bags in case
        case_bags = self.case_repo.get_bags_by_case(case_id)
        if not case_bags:
            raise ValueError(f"No bags found for case {case_id}")
        
        # Get primary bag
        primary_bag_id = None
        for cb in case_bags:
            if cb.primary_flag:
                primary_bag_id = cb.bag_id
                break
        if not primary_bag_id:
            primary_bag_id = case_bags[0].bag_id
        
        bag = self.bag_repo.get_by_id(primary_bag_id)
        if not bag:
            raise ValueError(f"Primary bag {primary_bag_id} not found")
        
        # Get journey and events for context
        journey = self.journey_repo.get_by_id(bag.journey_id)
        journey_legs = self.journey_repo.get_legs_by_journey(bag.journey_id)
        bag_events = self.bag_event_repo.get_by_bag(primary_bag_id)
        
        # Find onward leg
        onward_leg = None
        for leg in journey_legs:
            if leg.leg_status == "scheduled":
                onward_leg = leg
                break
        
        # Calculate freshness based on latest event age
        freshness_state = self._calculate_freshness(bag_events)
        
        # Generate recommendations based on case severity and time to deadline
        time_to_deadline = case.deadline_at - datetime.now(timezone.utc)
        minutes_to_deadline = int(time_to_deadline.total_seconds() / 60)
        
        recommendations = []
        
        # Recommendation 1: Priority transfer (high confidence for critical/high cases)
        if case.severity_code in ["critical", "high"] and minutes_to_deadline < 90:
            rec = self._create_priority_transfer_recommendation(
                case=case,
                bag=bag,
                onward_leg=onward_leg,
                bag_events=bag_events,
                freshness_state=freshness_state,
                minutes_to_deadline=minutes_to_deadline
            )
            recommendations.append(rec)
        
        # Recommendation 2: Monitor (alternative lower confidence)
        if case.severity_code in ["medium", "low"] or minutes_to_deadline > 60:
            rec = self._create_monitoring_recommendation(
                case=case,
                bag=bag,
                onward_leg=onward_leg,
                bag_events=bag_events,
                freshness_state=freshness_state,
                minutes_to_deadline=minutes_to_deadline
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _create_priority_transfer_recommendation(
        self,
        case,
        bag,
        onward_leg,
        bag_events,
        freshness_state,
        minutes_to_deadline
    ) -> Recommendation:
        """Create a priority transfer recommendation with high confidence."""
        # Build evidence
        evidence = {
            "bag_tag": bag.bag_tag,
            "time_to_deadline_minutes": minutes_to_deadline,
            "severity": case.severity_code,
            "latest_events": []
        }
        
        for event in bag_events[-3:]:  # Last 3 events
            evidence["latest_events"].append({
                "event_type": event.event_type,
                "station": event.event_station,
                "observed_at": event.observed_at.isoformat(),
                "fact_type": event.fact_type
            })
        
        if onward_leg:
            evidence["target_flight"] = onward_leg.flight_number
            evidence["target_gate"] = onward_leg.gate_code
            evidence["departure_at"] = onward_leg.scheduled_departure_at.isoformat()
        
        # Calculate confidence based on data freshness and time pressure
        confidence = Decimal("0.85")
        if freshness_state == "stale":
            confidence = Decimal("0.75")
        elif minutes_to_deadline < 45:
            confidence = Decimal("0.92")
        
        # Build reason text
        reason_text = (
            f"Bag requires expedited handling to meet {onward_leg.flight_number if onward_leg else 'connection'} "
            f"departure. With {minutes_to_deadline} minutes to cutoff and {case.severity_code} severity, "
            f"priority transfer minimizes misconnection risk."
        )
        
        # Create recommendation
        rec = Recommendation(
            id=str(uuid.uuid4()),
            case_id=case.id,
            action_code="PRIORITY_TRANSFER",
            action_label=f"Expedite Transfer to {onward_leg.gate_code if onward_leg else 'Connection Gate'}",
            reason_text=reason_text,
            confidence_score=confidence,
            freshness_state=freshness_state,
            evidence_json=json.dumps(evidence),
            generated_at=datetime.now(timezone.utc)
        )
        
        return self.rec_repo.create(rec)
    
    def _create_monitoring_recommendation(
        self,
        case,
        bag,
        onward_leg,
        bag_events,
        freshness_state,
        minutes_to_deadline
    ) -> Recommendation:
        """Create a monitoring recommendation with moderate confidence."""
        # Build evidence
        evidence = {
            "bag_tag": bag.bag_tag,
            "time_to_deadline_minutes": minutes_to_deadline,
            "severity": case.severity_code,
            "current_status": bag.current_status_code,
            "latest_events": []
        }
        
        for event in bag_events[-3:]:
            evidence["latest_events"].append({
                "event_type": event.event_type,
                "station": event.event_station,
                "observed_at": event.observed_at.isoformat(),
                "fact_type": event.fact_type
            })
        
        if onward_leg:
            evidence["target_flight"] = onward_leg.flight_number
            evidence["connection_window_minutes"] = minutes_to_deadline
        
        # Calculate confidence
        confidence = Decimal("0.72")
        if freshness_state == "fresh" and minutes_to_deadline > 120:
            confidence = Decimal("0.80")
        
        # Build reason text
        reason_text = (
            f"Current connection window of {minutes_to_deadline} minutes provides adequate buffer. "
            f"Continue monitoring for transfer scan confirmation. Escalate if no scan within 30 minutes."
        )
        
        # Create recommendation
        rec = Recommendation(
            id=str(uuid.uuid4()),
            case_id=case.id,
            action_code="MONITOR",
            action_label="Continue Monitoring Connection",
            reason_text=reason_text,
            confidence_score=confidence,
            freshness_state=freshness_state,
            evidence_json=json.dumps(evidence),
            generated_at=datetime.now(timezone.utc)
        )
        
        return self.rec_repo.create(rec)
    
    def _calculate_freshness(self, bag_events: list) -> str:
        """
        Calculate freshness state based on latest event age.
        
        Returns:
            "fresh" if latest event < 10 minutes old
            "stale" if latest event >= 10 minutes old
            "awaiting_confirmation" if no observed events
        """
        if not bag_events:
            return "awaiting_confirmation"
        
        # Find latest observed event
        latest_observed = None
        for event in reversed(bag_events):
            if event.fact_type == "observed":
                latest_observed = event
                break
        
        if not latest_observed:
            return "awaiting_confirmation"
        
        age = datetime.now(timezone.utc) - latest_observed.ingested_at
        if age.total_seconds() < 600:  # 10 minutes
            return "fresh"
        else:
            return "stale"
    
    def get_recommendations_for_case(
        self,
        case_id: str,
        include_superseded: bool = False
    ) -> list[Recommendation]:
        """Get all recommendations for a case."""
        return self.rec_repo.get_by_case(case_id, include_superseded=include_superseded)
    
    def supersede_recommendation(self, recommendation_id: str) -> Recommendation | None:
        """Mark a recommendation as superseded."""
        return self.rec_repo.supersede(recommendation_id)
