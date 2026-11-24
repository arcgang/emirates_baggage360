"""Recommendation repository for recommendation management."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.recommendation import Recommendation


class RecommendationRepository:
    """Repository for recommendation access and superseding."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, recommendation_id: str) -> Recommendation | None:
        """Get recommendation by ID."""
        return self.db.get(Recommendation, recommendation_id)
    
    def get_by_case(self, case_id: str, include_superseded: bool = False) -> list[Recommendation]:
        """
        Get all recommendations for a case.
        
        Args:
            case_id: Exception case ID
            include_superseded: If False, exclude superseded recommendations
        
        Returns:
            List of Recommendation records ordered by generated_at descending
        """
        stmt = select(Recommendation).where(Recommendation.case_id == case_id)
        
        if not include_superseded:
            stmt = stmt.where(Recommendation.superseded_at.is_(None))
        
        stmt = stmt.order_by(Recommendation.generated_at.desc())
        
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def create(self, recommendation: Recommendation) -> Recommendation:
        """Create a new recommendation."""
        self.db.add(recommendation)
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation
    
    def supersede(self, recommendation_id: str) -> Recommendation | None:
        """
        Mark a recommendation as superseded.
        Sets superseded_at to current timestamp.
        
        Args:
            recommendation_id: ID of recommendation to supersede
        
        Returns:
            Updated recommendation or None if not found
        """
        recommendation = self.get_by_id(recommendation_id)
        if not recommendation:
            return None
        
        recommendation.superseded_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation
    
    def supersede_all_for_case(self, case_id: str) -> int:
        """
        Supersede all active recommendations for a case.
        Useful when generating new recommendations to replace old ones.
        
        Args:
            case_id: Exception case ID
        
        Returns:
            Count of recommendations superseded
        """
        recommendations = self.get_by_case(case_id, include_superseded=False)
        count = 0
        for rec in recommendations:
            rec.superseded_at = datetime.now(timezone.utc)
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count
