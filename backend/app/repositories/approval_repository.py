"""Approval decision repository for approval management."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.approval import ApprovalDecision


class ApprovalRepository:
    """Repository for approval decision access and creation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, approval_id: str) -> ApprovalDecision | None:
        """Get approval decision by ID."""
        return self.db.get(ApprovalDecision, approval_id)
    
    def get_by_case_and_recommendation(
        self,
        case_id: str,
        recommendation_id: str
    ) -> ApprovalDecision | None:
        """
        Get approval decision for a specific case and recommendation.
        Returns the latest version if multiple exist.
        
        Args:
            case_id: Exception case ID
            recommendation_id: Recommendation ID
        
        Returns:
            Latest ApprovalDecision or None if not found
        """
        stmt = (
            select(ApprovalDecision)
            .where(
                ApprovalDecision.case_id == case_id,
                ApprovalDecision.recommendation_id == recommendation_id
            )
            .order_by(ApprovalDecision.decision_version.desc())
        )
        
        result = self.db.execute(stmt)
        return result.scalars().first()
    
    def get_by_case(self, case_id: str) -> list[ApprovalDecision]:
        """
        Get all approval decisions for a case.
        
        Args:
            case_id: Exception case ID
        
        Returns:
            List of ApprovalDecision records ordered by decided_at descending
        """
        stmt = (
            select(ApprovalDecision)
            .where(ApprovalDecision.case_id == case_id)
            .order_by(ApprovalDecision.decided_at.desc())
        )
        
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def create(
        self,
        case_id: str,
        recommendation_id: str,
        decided_by_user_id: str,
        decision_code: str,
        rationale_text: str | None = None
    ) -> ApprovalDecision:
        """
        Create a new approval decision.
        
        Enforces unique constraint on (case_id, recommendation_id, decision_version).
        Automatically increments decision_version if a prior decision exists.
        
        Args:
            case_id: Exception case ID
            recommendation_id: Recommendation ID
            decided_by_user_id: User ID of approver
            decision_code: 'approved' or 'rejected'
            rationale_text: Optional rationale for decision
        
        Returns:
            Created ApprovalDecision
        """
        # Check for existing decision to calculate version
        existing = self.get_by_case_and_recommendation(case_id, recommendation_id)
        decision_version = 1 if not existing else existing.decision_version + 1
        
        approval = ApprovalDecision(
            id=str(uuid.uuid4()),
            case_id=case_id,
            recommendation_id=recommendation_id,
            decided_by_user_id=decided_by_user_id,
            decision_code=decision_code,
            rationale_text=rationale_text,
            decided_at=datetime.now(timezone.utc),
            decision_version=decision_version
        )
        
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)
        return approval
