"""Exception case repository for case management and querying."""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ..models.exception_case import CaseBag, ExceptionCase


class ExceptionCaseRepository:
    """Repository for exception case aggregate and case-bag access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, case_id: str) -> ExceptionCase | None:
        """Get exception case by ID with relationships loaded."""
        stmt = (
            select(ExceptionCase)
            .where(ExceptionCase.id == case_id)
            .options(joinedload(ExceptionCase.case_bags))
        )
        result = self.db.execute(stmt)
        return result.unique().scalar_one_or_none()
    
    def get_by_reference(self, case_reference: str) -> ExceptionCase | None:
        """Get exception case by reference code."""
        stmt = select(ExceptionCase).where(ExceptionCase.case_reference == case_reference)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def list_prioritized(
        self,
        severity: str | None = None,
        station_scope: str | None = None,
        status_code: str | None = None,
        order_by_deadline: bool = True
    ) -> list[ExceptionCase]:
        """
        List exception cases with optional filters, ordered by priority.
        
        Args:
            severity: Filter by severity_code (critical, high, medium, low)
            station_scope: Filter by station (extracted from case metadata)
            status_code: Filter by status (open, under_review, approved, tasked, in_recovery, closed)
            order_by_deadline: If True, order by deadline ascending (most urgent first)
        
        Returns:
            List of ExceptionCase records
        """
        stmt = select(ExceptionCase)
        
        # Apply filters
        if severity:
            stmt = stmt.where(ExceptionCase.severity_code == severity)
        
        if status_code:
            stmt = stmt.where(ExceptionCase.status_code == status_code)
        
        # Order by deadline (most urgent first)
        if order_by_deadline:
            stmt = stmt.order_by(ExceptionCase.deadline_at.asc())
        else:
            stmt = stmt.order_by(ExceptionCase.created_at.desc())
        
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def create(self, case: ExceptionCase) -> ExceptionCase:
        """Create a new exception case."""
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case
    
    def update_status(self, case_id: str, new_status: str) -> ExceptionCase | None:
        """Update case status and updated_at timestamp."""
        case = self.get_by_id(case_id)
        if not case:
            return None
        
        case.status_code = new_status
        case.updated_at = datetime.now(timezone.utc)
        
        # If closing, set closed_at
        if new_status == "closed" and not case.closed_at:
            case.closed_at = datetime.now(timezone.utc)
        
        self.db.commit()
        self.db.refresh(case)
        return case
    
    def get_bags_by_case(self, case_id: str) -> list[CaseBag]:
        """Get all case-bag memberships for a case, ordered by primary flag."""
        stmt = (
            select(CaseBag)
            .where(CaseBag.case_id == case_id)
            .order_by(CaseBag.primary_flag.desc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def add_bag_to_case(self, case_id: str, bag_id: str, primary_flag: bool = False) -> CaseBag:
        """Add a bag to a case."""
        case_bag = CaseBag(
            case_id=case_id,
            bag_id=bag_id,
            primary_flag=primary_flag,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(case_bag)
        self.db.commit()
        self.db.refresh(case_bag)
        return case_bag
    
    def get_case_bag_count(self, case_id: str) -> int:
        """Get count of bags in a case."""
        stmt = select(func.count(CaseBag.bag_id)).where(CaseBag.case_id == case_id)
        result = self.db.execute(stmt)
        return result.scalar() or 0
