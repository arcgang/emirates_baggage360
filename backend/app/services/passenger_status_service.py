"""Passenger status service for passenger-safe bag and case status composition."""
import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from ..repositories.bag_repository import BagEventRepository, BagRepository
from ..repositories.exception_case_repository import ExceptionCaseRepository
from ..repositories.passenger_view_repository import PassengerViewRepository
from ..schemas.passenger_schemas import (
    PassengerBagStatus,
    PassengerCaseStatus,
    PassengerProgressStep,
)

if TYPE_CHECKING:
    from ..models.passenger_view import PassengerCaseView


class PassengerStatusService:
    """
    Service for composing passenger-safe bag status views.
    
    Implements FR-012: passenger baggage status view with confirmed milestones.
    Implements FR-013: separation of confirmed vs estimated passenger information.
    Applies passenger-safe filtering: excludes internal notes, risk scores, and unauthorized details.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.bag_repo = BagRepository(db)
        self.bag_event_repo = BagEventRepository(db)
        self.case_repo = ExceptionCaseRepository(db)
        self.passenger_view_repo = PassengerViewRepository(db)
    
    def compose_bag_status_for_passenger(self, bag_tag: str) -> PassengerBagStatus | None:
        """
        Compose passenger-safe bag status for a bag tag.
        
        Applies passenger-safe filtering per FR-012:
        - Returns latest confirmed milestone with source system label
        - Returns estimated next step with explicit uncertainty explanation
        - Returns delayed bag case reference if case exists
        - Returns next expected update timestamp
        - Excludes internal notes and risk scores
        
        Args:
            bag_tag: Bag tag identifier (e.g., EK001234567, 0176482193)
        
        Returns:
            PassengerBagStatus or None if bag not found
        """
        # Find bag by tag
        bag = self.bag_repo.get_by_tag(bag_tag)
        if not bag:
            return None
        
        # Get latest confirmed bag event (observed fact_type only)
        events = self.bag_event_repo.get_by_bag(bag.id)
        # Filter for observed events and reverse to get latest first (get_by_bag returns ascending order)
        confirmed_events = [e for e in reversed(events) if e.fact_type == "observed"]
        
        if not confirmed_events:
            # No confirmed events, return basic status with bag's current status
            status_label = self._get_passenger_safe_status_label(bag.current_status_code)
            return PassengerBagStatus(
                bag_tag=bag_tag,
                latest_confirmed_milestone="Bag checked in",
                status_label=status_label,
                estimated_notice=None,
                delayed_case_reference=None,
                next_expected_update=None,
                last_updated_at=datetime.now(timezone.utc)
            )
        
        # Get latest confirmed event
        latest_event = confirmed_events[0]  # Already ordered by observed_at desc
        
        # Compose latest confirmed milestone with source system label
        latest_confirmed_milestone = self._format_milestone_for_passenger(latest_event)
        
        # Determine status label based on bag status
        status_label = self._get_passenger_safe_status_label(bag.current_status_code)
        
        # Check if bag is part of an exception case
        delayed_case_reference = None
        estimated_notice = None
        next_expected_update = None
        
        if bag.current_case_id:
            # Get passenger case view for this case
            case_view = self.passenger_view_repo.get_by_case_id(bag.current_case_id)
            if case_view:
                delayed_case_reference = case_view.case_reference
                estimated_notice = case_view.estimated_notice
                next_expected_update = case_view.next_expected_update
        
        return PassengerBagStatus(
            bag_tag=bag_tag,
            latest_confirmed_milestone=latest_confirmed_milestone,
            status_label=status_label,
            estimated_notice=estimated_notice,
            delayed_case_reference=delayed_case_reference,
            next_expected_update=next_expected_update,
            last_updated_at=latest_event.observed_at
        )
    
    def _format_milestone_for_passenger(self, event) -> str:
        """
        Format bag event as passenger-readable milestone.
        
        Includes source system label and plain language description.
        """
        # Format timestamp as human-readable
        time_str = event.observed_at.strftime("%H:%M")
        date_str = event.observed_at.strftime("%d %b")
        
        # Map event type to passenger-friendly text
        event_text_map = {
            "acceptance": "Checked in",
            "transfer_scan": "Scanned at transfer area",
            "load": "Loaded onto aircraft",
            "arrival": "Arrived at destination",
            "delivery": "Available for collection",
            "custody_handover": "In baggage service care"
        }
        
        event_text = event_text_map.get(event.event_type, event.event_type.replace("_", " ").title())
        
        # Add location if available
        location_text = f" at {event.event_station}" if event.event_station else ""
        
        return f"{event_text}{location_text} {time_str} {date_str} ({event.source_system})"
    
    def _get_passenger_safe_status_label(self, status_code: str) -> str:
        """
        Get passenger-safe status label from internal status code.
        
        Maps internal status codes to plain language suitable for passenger understanding.
        """
        status_map = {
            "checked_in": "Checked in",
            "in_transfer": "In transit",
            "loaded": "On aircraft",
            "arrived": "Arrived",
            "delivered": "Available for collection",
            "at_risk": "Being monitored",
            "exception": "Delayed - recovery in progress"
        }
        
        return status_map.get(status_code, "In transit")
    
    def compose_case_status_for_passenger(self, case_reference: str) -> PassengerCaseStatus | None:
        """
        Compose passenger-safe case status for a delayed-bag case reference.
        
        Implements FR-013 and FR-014: passenger case status with confirmed/estimated separation.
        Returns 404 (None) for unauthorized case references to prevent information leakage.
        
        Applies passenger-safe filtering per FR-013:
        - Returns latest confirmed status as plain-language description
        - Returns estimated notice with explicit uncertainty labeling
        - Returns progress steps marked as confirmed or estimated
        - Returns next expected update timestamp
        - Excludes internal operational notes and risk scores
        
        Args:
            case_reference: Case reference identifier (e.g., BC-DXB-240611)
        
        Returns:
            PassengerCaseStatus or None if case not found/unauthorized
        """
        # Get passenger case view by case reference
        case_view = self.passenger_view_repo.get_by_case_reference(case_reference)
        if not case_view:
            # Return None to signal 404 - prevents information leakage for unauthorized references
            return None
        
        # Parse passenger-safe payload
        passenger_payload = json.loads(case_view.passenger_safe_payload_json)
        
        # Build progress steps from payload
        progress_steps = []
        for step_data in passenger_payload.get("progress_steps", []):
            progress_steps.append(PassengerProgressStep(
                step_text=step_data["step_text"],
                status=step_data["status"],  # "confirmed" or "estimated"
                timestamp=datetime.fromisoformat(step_data["timestamp"]) if step_data.get("timestamp") else None,
                uncertainty_note=step_data.get("uncertainty_note")
            ))
        
        # Compose response
        return PassengerCaseStatus(
            case_reference=case_reference,
            latest_confirmed_status=case_view.latest_confirmed_status,
            estimated_notice=case_view.estimated_notice,
            next_expected_update=case_view.next_expected_update,
            progress_steps=progress_steps,
            last_updated_at=case_view.refreshed_at
        )
    
    def refresh_passenger_view(self, case_id: str) -> "PassengerCaseView | None":
        """
        Refresh passenger case view from current exception case, bags, and recommendations state.
        
        Idempotent refresh operation that recomputes passenger-safe status from source tables.
        Called when case state changes (approval, task completion, case closure).
        
        Args:
            case_id: Exception case ID
        
        Returns:
            Refreshed PassengerCaseView or None if case not found
        """
        # Get exception case
        case = self.case_repo.get_by_id(case_id)
        if not case:
            return None
        
        # Recompute passenger-safe payload from current case state
        # Get case bags and their latest events
        case_bags = self.case_repo.get_bags_by_case(case_id)
        
        progress_steps = []
        
        # Add confirmed arrival step based on bag events
        if case_bags:
            first_bag_id = case_bags[0].bag_id
            first_bag = self.bag_repo.get_by_id(first_bag_id)
            if first_bag:
                arrival_events = [e for e in self.bag_event_repo.get_by_bag(first_bag.id) 
                                if e.event_type == "arrived" and e.fact_type == "observed"]
                if arrival_events:
                    latest_arrival = max(arrival_events, key=lambda e: e.observed_at)
                    progress_steps.append({
                        "step_text": f"Arrived at Dubai {latest_arrival.observed_at.strftime('%H:%M')} GST",
                        "status": "confirmed",
                        "timestamp": latest_arrival.observed_at.isoformat()
                    })
        
        # Add estimated prioritization step based on case severity
        if case.severity_code in ["critical", "high"]:
            progress_steps.append({
                "step_text": "Being prioritised for onward flight",
                "status": "estimated",
                "timestamp": None,
                "uncertainty_note": "Estimated based on current operational priority"
            })
        
        # Build estimated notice based on case status
        estimated_notice = None
        if case.status_code == "open":
            if case.severity_code == "critical":
                estimated_notice = "Being prioritised for onward flight. Estimated notice: delivery to gate within 60 minutes"
            elif case.severity_code == "high":
                estimated_notice = "Being monitored for timely transfer. Expected update within 90 minutes"
        elif case.status_code == "closed":
            # Case closed - confirmed delivery
            estimated_notice = None
            # Update progress steps to show confirmed delivery
            if case.observed_state_summary and "Delivered" in case.observed_state_summary:
                progress_steps.append({
                    "step_text": case.observed_state_summary,
                    "status": "confirmed",
                    "timestamp": case.closed_at.isoformat() if case.closed_at else None
                })
        
        # Determine next expected update
        next_expected_update = "2 hours before departure"
        if case.status_code == "closed":
            next_expected_update = "Case resolved"
        
        # Build passenger-safe payload
        passenger_safe_payload = {
            "progress_steps": progress_steps,
            "case_status": case.status_code,
            "severity": case.severity_code
        }
        
        # Update or create passenger case view
        existing_view = self.passenger_view_repo.get_by_case_id(case_id)
        
        if existing_view:
            # Update existing view
            existing_view.latest_confirmed_status = progress_steps[0]["step_text"] if progress_steps and progress_steps[0]["status"] == "confirmed" else "Baggage in recovery process"
            existing_view.estimated_notice = estimated_notice
            existing_view.next_expected_update = next_expected_update
            existing_view.passenger_safe_payload_json = json.dumps(passenger_safe_payload)
            existing_view.refreshed_at = datetime.now(timezone.utc)
            self.db.commit()
            return existing_view
        else:
            # Create new view
            import uuid

            from ..models.passenger_view import PassengerCaseView
            
            new_view = PassengerCaseView(
                id=str(uuid.uuid4()),
                case_id=case_id,
                case_reference=case.case_reference,
                latest_confirmed_status=progress_steps[0]["step_text"] if progress_steps and progress_steps[0]["status"] == "confirmed" else "Baggage in recovery process",
                estimated_notice=estimated_notice,
                next_expected_update=next_expected_update,
                passenger_safe_payload_json=json.dumps(passenger_safe_payload),
                refreshed_at=datetime.now(timezone.utc)
            )
            self.db.add(new_view)
            self.db.commit()
            return new_view
