# TASK-9 Handoff: Passenger Delayed-Bag Case Status

## Overview
Completed passenger delayed-bag case status composition service implementing FR-013 and FR-014. This task provides passenger-safe case status with confirmed vs estimated separation, explicit uncertainty labeling, and progress steps.

## Service Layer Implementation

### PassengerStatusService Extensions

**New Method: `compose_case_status_for_passenger(case_reference: str)`**
- Composes passenger-safe case status for a delayed-bag case reference
- Returns `PassengerCaseStatus` with:
  - `case_reference`: Case reference identifier (e.g., BC-DXB-240611)
  - `latest_confirmed_status`: Plain-language confirmed status description
  - `estimated_notice`: Explicit uncertainty labeling when applicable (nullable)
  - `next_expected_update`: Next expected update timestamp
  - `progress_steps`: List of `PassengerProgressStep` marked as "confirmed" or "estimated"
  - `last_updated_at`: Last refresh timestamp
- Returns `None` for unauthorized case references to prevent information leakage (404 behavior)
- Excludes internal operational notes and risk scores

**New Method: `refresh_passenger_view(case_id: str)`**
- Idempotent refresh operation recomputing passenger-safe status from exception_case + bags + recommendations state
- Creates new `PassengerCaseView` if none exists, updates existing view otherwise
- Recomputes progress steps from current bag events and case state
- Called when case state changes (approval, task completion, case closure)
- Returns refreshed `PassengerCaseView` or `None` if case not found

### PassengerViewRepository

**Existing Methods (confirmed available):**
- `get_by_case_id(case_id: str)`: Get passenger case view by case ID
- `get_by_case_reference(case_reference: str)`: Get passenger case view by case reference

## Schema Definitions

### PassengerProgressStep (new)
```python
class PassengerProgressStep(BaseModel):
    step_text: str                      # Plain-language progress step
    status: str                         # "confirmed" or "estimated"
    timestamp: datetime | None          # Optional timestamp for confirmed steps
    uncertainty_note: str | None        # Explicit uncertainty explanation for estimated steps
```

### PassengerCaseStatus (new)
```python
class PassengerCaseStatus(BaseModel):
    case_reference: str                 # Case reference (e.g., BC-DXB-240611)
    latest_confirmed_status: str        # Latest confirmed status in plain language
    estimated_notice: str | None        # Estimated notice with uncertainty labeling (nullable)
    next_expected_update: str           # Next expected update timestamp or message
    progress_steps: list[PassengerProgressStep]  # Progress steps marked confirmed/estimated
    last_updated_at: datetime           # Last refresh timestamp
```

## Seed Data

### Passenger Case Views
Two test scenarios seeded in `passenger_case_views` table:

**1. BC-DXB-240611 (Delayed-bag case with estimated status)**
- Case reference: `BC-DXB-240611`
- Latest confirmed status: `"Arrived at Dubai 19:58 GST"`
- Estimated notice: `"Being prioritised for onward flight. Estimated notice: delivery to gate within 60 minutes"`
- Next expected update: `"2 hours before departure"`
- Progress steps:
  1. `"Arrived at Dubai 19:58 GST"` (confirmed, with timestamp)
  2. `"Being prioritised for onward flight"` (estimated, uncertainty note: "Estimated based on current operational priority")

**2. BC-DXB-240612 (Closed case with confirmed delivery)**
- Case reference: `BC-DXB-240612`
- Latest confirmed status: `"Delivered to belt 5"`
- Estimated notice: `None` (closed cases have no estimated notice)
- Next expected update: `"Case resolved"`
- Progress steps:
  1. `"Arrived at Dubai 19:03 GST"` (confirmed, with timestamp)
  2. `"Scanned at transfer area 19:17 GST"` (confirmed, with timestamp)
  3. `"Delivered to belt 5"` (confirmed, with timestamp)

## Passenger-Safe Filtering Rules

### Excludes (never exposed to passengers):
- Internal operational notes
- Risk scores (confidence_score, urgency_rank)
- Alternative recommendation rationale
- Unrelated passenger details
- Raw predicted_state_summary from exception cases

### Includes (passenger-safe):
- Confirmed baggage events with source system labels
- Plain-language status descriptions
- Explicit uncertainty labels for estimated/predicted information
- Progress steps marked as "confirmed" or "estimated"
- Next expected update timestamp

## FR Acceptance Coverage

### FR-013: Separation of confirmed vs estimated passenger information
- ✓ Estimated information labeled distinctly from confirmed events (`status: "confirmed"` vs `status: "estimated"`)
- ✓ Explicit uncertainty explanation included when only prediction available (`uncertainty_note` field)
- ✓ No unconfirmed delivery outcomes presented as guarantees (closed cases only show confirmed delivery)

### FR-014: Delayed-bag case status and next steps
- ✓ Shows delayed-bag case reference when such a case exists (`case_reference` field)
- ✓ Displays progress state and next expected step (`progress_steps` with explicit status markers)
- ✓ Delivery expectations presented only when supported by authorized and fresh source information (confirmed steps have timestamps, estimated steps have uncertainty notes)

## Test Coverage

### test_passenger_status_service.py (6 tests)
1. `test_compose_case_status_returns_confirmed_and_estimated_steps` - Verifies response includes both confirmed and estimated progress steps with correct markers
2. `test_compose_case_status_excludes_internal_notes` - Verifies internal operational notes and risk scores are excluded from passenger view
3. `test_compose_case_status_returns_404_for_unauthorized_reference` - Verifies unauthorized case references return None (404 behavior)
4. `test_compose_case_status_handles_closed_case_with_confirmed_delivery` - Verifies closed cases show only confirmed delivery without estimated notice
5. `test_refresh_passenger_view_creates_new_view_idempotently` - Verifies refresh creates new view when none exists
6. `test_refresh_passenger_view_updates_existing_view` - Verifies refresh updates existing view idempotently

## Integration Notes for Future Tasks

### No API Endpoint Added
This task implements **service layer, repository layer, and schema layer only**. No API endpoint is added in this task. Future backend API tasks can integrate these services when implementing passenger-facing routes.

The passenger case status endpoint is NOT implemented in this task. A future task will add the API route.

### Expected Integration Pattern (for future implementation)
When a future task implements the passenger case status endpoint:
1. Create route handler in passenger router
2. Extract `case_reference` from path parameter
3. Call `PassengerStatusService.compose_case_status_for_passenger(case_reference)`
4. Return `PassengerCaseStatus` schema (200) or 404 if service returns `None`
5. Apply authentication middleware (passenger role required)

### Refresh Trigger Points
Call `refresh_passenger_view(case_id)` when:
- Approval decision recorded (case state changes from open to approved)
- Task completion submitted (task evidence recorded with completion)
- Case closure (case status changes to closed)
- Bag events added/updated for bags in the case

## Related Files Modified
- `/repos/emirates_baggage360/backend/app/services/passenger_status_service.py` - Extended with case status composition and view refresh
- `/repos/emirates_baggage360/backend/app/schemas/passenger_schemas.py` - Added `PassengerProgressStep` and `PassengerCaseStatus` schemas
- `/repos/emirates_baggage360/backend/app/seed.py` - Extended `seed_passenger_case_views` with test scenarios
- `/repos/emirates_baggage360/backend/tests/test_passenger_status_service.py` - Added 6 comprehensive tests
