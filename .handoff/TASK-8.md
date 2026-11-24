# TASK-8 Handoff: Backend Feature B6 - Task Acknowledgement and Passenger Bag Status

## Implementation Summary

This task implements the **service layer**, **repository layer**, and **schema layer** for task acknowledgement and passenger bag status features. 

**API endpoints are NOT part of this task.** The router/endpoint implementation will be completed in a future backend API task.

## Completed Services

### TaskDispatchService
Extended with task event acceptance method `accept_task_event()`:
- Accepts event types: acknowledged, in_progress, completed, evidence_submitted, blocked
- Updates task status based on event type
- Propagates status changes to parent case when task evidence changes case state
- Commits evidence and task update atomically with audit event
- Returns tuple of (TaskEvidence or None for idempotent replay, updated Task, case_status)

### PassengerStatusService
New service for composing passenger-safe bag status views:
- `compose_bag_status_for_passenger(bag_tag)` - returns passenger-safe bag status
- Applies passenger-safe filtering per FR-012:
  - Latest confirmed milestone with source system label
  - Estimated next step with explicit uncertainty explanation
  - Delayed bag case reference if case exists
  - Next expected update timestamp
  - Excludes internal notes and risk scores
- Uses only observed events (fact_type=observed) for confirmed milestones
- Maps internal status codes to plain language labels

## Repositories

### TaskEvidenceRepository
New repository for task evidence management:
- `create()` - creates task evidence with idempotent replay support via unique client_event_id
- `list_by_task(task_id)` - returns all evidence for a task ordered by recorded_at desc
- Returns None on duplicate client_event_id for idempotent replay

### PassengerViewRepository
New repository for passenger case view access:
- `get_by_case_id(case_id)` - returns passenger case view by case ID
- `get_by_case_reference(case_reference)` - returns passenger case view by case reference

## Schemas

### Partner Schemas (partner_schemas.py)
Extended with:
- `TaskEventRequest` - request for task event submission with event_type, client_event_id, note, evidence_type, evidence_reference
- `TaskEventResponse` - response with task_id, event_type, recorded_at, case_status

### Passenger Schemas (passenger_schemas.py)
New schemas for passenger-facing views:
- `PassengerMilestone` - passenger-visible milestone with source system label
- `PassengerBagStatus` - passenger bag status with confirmed milestone and estimated next step

## Seed Data

### Task Evidence
Seed includes:
- Acknowledgement for TSK-DXB-1181 with scan confirmation (CLIENT-EVT-001)
- In-progress updates for TSK-DXB-1176 with scan confirmation (CLIENT-EVT-002, CLIENT-EVT-003)
- Evidence submission with handover proof for TSK-DXB-1181 (CLIENT-EVT-004)

### Passenger Case Views
Seed includes:
- BC-DXB-240611 (case1): "Arrived at Dubai 19:58 GST", estimated "Being prioritised for onward flight"
- BC-DXB-240612 (case2): "Arrived at Dubai 19:03 GST, scanned at transfer area", estimated delivery within 90 minutes

### Passenger-Friendly Bags
Seed includes:
- Bag tag 0176482193: at-risk with estimated status, linked to case1
- Bag tag 0176482194: on-time with confirmed status
- Both bags have observed events for passenger scenario testing

## Service Layer API

### TaskDispatchService.accept_task_event()
```python
accept_task_event(
    task_id: str,
    actor_user_id: str,
    event_type: str,  # acknowledged, in_progress, completed, evidence_submitted, blocked
    note_text: str | None,
    evidence_type: str | None,  # scan_confirmation, handover_proof, completion_note
    evidence_reference: str | None,
    client_event_id: str
) -> tuple[TaskEvidence | None, Task, str]
```

**Returns:**
- TaskEvidence or None (None for idempotent replay when client_event_id exists)
- Updated Task with new status
- Case status string (open, tasked, in_recovery, closed)

**Status Transitions:**
- acknowledged → task status becomes "acknowledged"
- in_progress → task status becomes "in_progress"
- completed or evidence_submitted → task status becomes "completed"
- blocked → task status resets to "assigned"

**Case Status Updates:**
- When first task completes: case status becomes "in_recovery"
- When all tasks complete: case status becomes "closed"

### PassengerStatusService.compose_bag_status_for_passenger()
```python
compose_bag_status_for_passenger(bag_tag: str) -> PassengerBagStatus | None
```

**Returns PassengerBagStatus:**
```python
{
    "bag_tag": str,
    "latest_confirmed_milestone": str,  # e.g., "Arrived at DXB 19:58 (Wasla)"
    "status_label": str,  # passenger-safe label
    "estimated_notice": str | None,  # from case view if exists
    "delayed_case_reference": str | None,  # e.g., "BC-DXB-240611"
    "next_expected_update": str | None,
    "last_updated_at": datetime
}
```

**Passenger-Safe Status Labels:**
- checked_in → "Checked in"
- in_transfer → "In transit"
- loaded → "On aircraft"
- arrived → "Arrived"
- delivered → "Available for collection"
- at_risk → "Being monitored"
- exception → "Delayed - recovery in progress"

## Seed References

### Seed Bag Tags for Passenger Scenarios
- **0176482193**: At-risk bag with estimated status, linked to case BC-DXB-240611
- **0176482194**: On-time bag with confirmed status

### Seed Tasks with Evidence
- **TSK-DXB-1181**: Acknowledged with scan confirmation
- **TSK-DXB-1176**: In progress with multiple evidence submissions
- **TSK-DXB-1187, TSK-DXB-1189**: Assigned, no evidence yet

### Seed Case Views
- **BC-DXB-240611**: "Arrived at Dubai 19:58 GST", estimated "Being prioritised for onward flight"
- **BC-DXB-240612**: "Arrived at Dubai 19:03 GST, scanned at transfer area", estimated delivery within 90 minutes

## Testing

### Test Coverage
- Task event submission with acknowledged, in_progress, completed event types
- Idempotent replay via client_event_id returns None on duplicate
- Task status updates propagate to parent case status
- Completed tasks trigger case status update to in_recovery
- All tasks completed triggers case status update to closed
- Passenger status composition returns confirmed milestones only
- Passenger status excludes derived/estimated events from milestones
- Passenger status includes case reference and estimated notice when bag in case
- Passenger-safe status labels map internal codes to plain language

### Test Files
- `tests/test_task_dispatch_service.py` (6 tests)
- `tests/test_passenger_status_service.py` (6 tests)

## Future Integration Notes

Both `TaskDispatchService.accept_task_event()` and `PassengerStatusService.compose_bag_status_for_passenger()` are fully tested and ready for future route integration when partner and passenger API endpoints are implemented in a later task.
