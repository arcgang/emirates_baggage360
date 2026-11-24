"""Passenger baggage status and delayed-bag case status router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..schemas.passenger_schemas import PassengerBagStatus, PassengerCaseStatus
from ..services.passenger_status_service import PassengerStatusService
from ..models.bag import Bag
from ..models.journey import PassengerJourney

router = APIRouter(prefix="/passenger")


class BagListItem(BaseModel):
    bag_tag: str
    flight_number: str
    status: str
    last_location: str | None = None


class BagListResponse(BaseModel):
    bags: list[BagListItem]


@router.get("/bags", response_model=BagListResponse)
def list_passenger_bags(
    db: Session = Depends(get_db)
):
    """
    List all bags for the authenticated passenger.
    
    For demo purposes, returns all bags. In production, would filter by passenger ID.
    """
    bags = db.query(Bag).join(PassengerJourney).limit(50).all()
    
    items = []
    for bag in bags:
        # Get latest event for location
        last_event = None
        if bag.events:
            last_event = max(bag.events, key=lambda e: e.observed_at)
        
        items.append(BagListItem(
            bag_tag=bag.bag_tag,
            flight_number=bag.journey.flight_number if bag.journey else "Unknown",
            status=bag.current_status_code,
            last_location=last_event.event_station if last_event else None
        ))
    
    return BagListResponse(bags=items)


@router.get("/bags/{bag_tag}/status", response_model=PassengerBagStatus)
def get_passenger_bag_status(
    bag_tag: str,
    db: Session = Depends(get_db)
):
    """
    Get passenger-safe baggage status for a bag tag.
    
    Returns:
        - Latest confirmed milestone with source system label
        - Estimated next step with explicit uncertainty explanation
        - Delayed bag case reference if case exists
        - Next expected update timestamp
        - Excludes internal notes and risk scores
    """
    service = PassengerStatusService(db)
    status = service.compose_bag_status_for_passenger(bag_tag)
    
    if status is None:
        raise HTTPException(
            status_code=404,
            detail=f"Bag {bag_tag} not found or not visible to passenger"
        )
    
    return status


@router.get("/cases/{case_reference}", response_model=PassengerCaseStatus)
def get_passenger_case_status(
    case_reference: str,
    db: Session = Depends(get_db)
):
    """
    Get passenger-safe delayed-bag case status.
    
    Returns:
        - Case reference and plain-language status
        - Confirmed vs estimated progress steps with visual distinction
        - Next expected milestone with uncertainty explanation
        - Excludes internal operational notes and risk scores
    """
    service = PassengerStatusService(db)
    status = service.compose_case_status_for_passenger(case_reference)
    
    if status is None:
        raise HTTPException(
            status_code=404,
            detail=f"Case {case_reference} not found or not visible to passenger"
        )
    
    return status
