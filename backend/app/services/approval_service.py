"""Approval service for recording human approval decisions."""
from sqlalchemy.orm import Session

from ..repositories.approval_repository import ApprovalRepository
from ..repositories.exception_case_repository import ExceptionCaseRepository
from ..repositories.recommendation_repository import RecommendationRepository


class ApprovalService:
    """
    Service for recording human-in-the-loop approval decisions.
    
    Enforces FR-007: approval is mandatory before task dispatch.
    Records approver identity, timestamp, decision code (approved/rejected),
    and optional rationale.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.approval_repo = ApprovalRepository(db)
        self.case_repo = ExceptionCaseRepository(db)
        self.rec_repo = RecommendationRepository(db)
    
    def record_approval_decision(
        self,
        case_id: str,
        recommendation_id: str,
        decided_by_user_id: str,
        decision_code: str,
        rationale_text: str | None = None
    ):
        """
        Record an approval or rejection decision for a recommendation.
        
        Validates that the case and recommendation exist before creating
        the approval decision. Enforces unique constraint on
        (case_id, recommendation_id, decision_version).
        
        Only approved decisions trigger task creation (handled by TaskDispatchService).
        
        Args:
            case_id: Exception case ID
            recommendation_id: Recommendation ID
            decided_by_user_id: User ID of approver
            decision_code: 'approved' or 'rejected'
            rationale_text: Optional rationale for decision
        
        Returns:
            Created ApprovalDecision
        
        Raises:
            ValueError: If case or recommendation not found
            ValueError: If decision_code invalid
        """
        # Validate inputs
        if decision_code not in ["approved", "rejected"]:
            raise ValueError(f"Invalid decision_code: {decision_code}. Must be 'approved' or 'rejected'.")
        
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        # Verify recommendation exists and belongs to case
        recommendation = self.rec_repo.get_by_id(recommendation_id)
        if not recommendation:
            raise ValueError(f"Recommendation {recommendation_id} not found")
        
        if recommendation.case_id != case_id:
            raise ValueError(f"Recommendation {recommendation_id} does not belong to case {case_id}")
        
        # Create approval decision
        approval = self.approval_repo.create(
            case_id=case_id,
            recommendation_id=recommendation_id,
            decided_by_user_id=decided_by_user_id,
            decision_code=decision_code,
            rationale_text=rationale_text
        )
        
        return approval
    
    def get_approval_for_recommendation(
        self,
        case_id: str,
        recommendation_id: str
    ):
        """
        Get the latest approval decision for a recommendation.
        
        Args:
            case_id: Exception case ID
            recommendation_id: Recommendation ID
        
        Returns:
            ApprovalDecision or None if no decision exists
        """
        return self.approval_repo.get_by_case_and_recommendation(case_id, recommendation_id)
    
    def is_approved(self, case_id: str, recommendation_id: str) -> bool:
        """
        Check if a recommendation has been approved.
        
        Args:
            case_id: Exception case ID
            recommendation_id: Recommendation ID
        
        Returns:
            True if latest decision is 'approved', False otherwise
        """
        approval = self.get_approval_for_recommendation(case_id, recommendation_id)
        return approval is not None and approval.decision_code == "approved"
