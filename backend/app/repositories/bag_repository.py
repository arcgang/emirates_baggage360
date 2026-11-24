"""Bag repository for bag and bag event access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.bag import Bag, BagEvent


class BagRepository:
    """Repository for bag aggregate and bag event access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_tag(self, bag_tag: str) -> Bag | None:
        """Get bag by bag tag."""
        stmt = select(Bag).where(Bag.bag_tag == bag_tag)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_id(self, bag_id: str) -> Bag | None:
        """Get bag by ID."""
        return self.db.get(Bag, bag_id)
    
    def list_by_case(self, case_id: str) -> list[Bag]:
        """Get all bags associated with a case."""
        from ..models.exception_case import CaseBag
        
        stmt = (
            select(Bag)
            .join(CaseBag, CaseBag.bag_id == Bag.id)
            .where(CaseBag.case_id == case_id)
            .order_by(CaseBag.primary_flag.desc(), Bag.bag_tag)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())


class BagEventRepository:
    """Repository for bag event access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_bag(self, bag_id: str) -> list[BagEvent]:
        """Get all events for a bag, ordered by observed_at."""
        stmt = (
            select(BagEvent)
            .where(BagEvent.bag_id == bag_id)
            .order_by(BagEvent.observed_at.asc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def create(self, bag_event: BagEvent) -> BagEvent:
        """Create a new bag event."""
        self.db.add(bag_event)
        self.db.commit()
        self.db.refresh(bag_event)
        return bag_event
    
    def list_latest_by_bags(self, bag_ids: list[str]) -> dict[str, BagEvent]:
        """
        Get the latest event for each bag.
        Returns a dict mapping bag_id to latest BagEvent.
        Freshness is calculated based on observed_at relative to now.
        """
        from datetime import datetime, timedelta, timezone

        from sqlalchemy import func
        
        # Subquery to get the latest observed_at per bag
        subq = (
            select(
                BagEvent.bag_id,
                func.max(BagEvent.observed_at).label("max_observed_at")
            )
            .where(BagEvent.bag_id.in_(bag_ids))
            .group_by(BagEvent.bag_id)
            .subquery()
        )
        
        # Join to get the full event records
        stmt = (
            select(BagEvent)
            .join(
                subq,
                (BagEvent.bag_id == subq.c.bag_id) &
                (BagEvent.observed_at == subq.c.max_observed_at)
            )
        )
        result = self.db.execute(stmt)
        events = result.scalars().all()
        
        # Calculate freshness state
        now = datetime.now(timezone.utc)
        freshness_threshold = timedelta(minutes=30)
        
        event_map = {}
        for event in events:
            age = now - event.observed_at
            if age > freshness_threshold:
                event.freshness_state = "stale"
            else:
                event.freshness_state = "fresh"
            event_map[event.bag_id] = event
        
        return event_map
    
    def calculate_freshness_state(self, event: BagEvent) -> str:
        """
        Calculate freshness state for a bag event.
        
        Thresholds:
        - fresh: < 10 minutes since ingested_at
        - stale: >= 10 minutes since ingested_at
        - awaiting_confirmation: no event yet seen (ingested_at is None or event is derived)
        
        Args:
            event: BagEvent to evaluate
        
        Returns:
            One of: "fresh", "stale", "awaiting_confirmation"
        """
        from datetime import datetime, timedelta, timezone
        
        # If event is not observed (derived/estimated), mark as awaiting confirmation
        if event.fact_type in ["derived", "estimated"]:
            return "awaiting_confirmation"
        
        # Calculate age based on ingested_at
        now = datetime.now(timezone.utc)
        # Ensure ingested_at is timezone-aware for comparison
        ingested = event.ingested_at.replace(tzinfo=timezone.utc) if event.ingested_at.tzinfo is None else event.ingested_at
        age = now - ingested
        
        # Thresholds
        fresh_threshold = timedelta(minutes=10)
        
        if age < fresh_threshold:
            return "fresh"
        else:
            return "stale"
