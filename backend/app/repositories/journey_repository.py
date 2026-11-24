"""Journey repository for passenger journey and leg access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.journey import JourneyLeg, PassengerJourney


class JourneyRepository:
    """Repository for passenger journey access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, journey_id: str) -> PassengerJourney | None:
        """Get passenger journey by ID."""
        return self.db.get(PassengerJourney, journey_id)
    
    def get_legs_by_journey(self, journey_id: str) -> list[JourneyLeg]:
        """Get all legs for a journey, ordered by sequence number."""
        stmt = (
            select(JourneyLeg)
            .where(JourneyLeg.journey_id == journey_id)
            .order_by(JourneyLeg.sequence_number.asc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
