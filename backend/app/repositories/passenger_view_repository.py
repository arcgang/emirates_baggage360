"""Passenger view repository for passenger-safe case status projections."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.passenger_view import PassengerCaseView


class PassengerViewRepository:
    """Repository for passenger-safe case view access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_case_id(self, case_id: str) -> PassengerCaseView | None:
        """
        Get passenger case view by case ID.
        
        Args:
            case_id: Exception case ID
        
        Returns:
            PassengerCaseView or None if not found
        """
        stmt = select(PassengerCaseView).where(PassengerCaseView.case_id == case_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_case_reference(self, case_reference: str) -> PassengerCaseView | None:
        """
        Get passenger case view by case reference.
        
        Args:
            case_reference: Case reference (e.g., BC-DXB-240611)
        
        Returns:
            PassengerCaseView or None if not found
        """
        stmt = select(PassengerCaseView).where(PassengerCaseView.case_reference == case_reference)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
