# TASK-6 Handoff: Approval and Task Dispatch

## Completed Implementation

This task implemented human-in-the-loop approval and operational task dispatch services for the Baggage360 system, covering FR-007 (approval requirement) and FR-008 (task dispatch).

## Approval Flow

### POST /api/v1/operations/cases/{case_id}/approvals

**Route implemented in**: `app/routers/operations.py`, mounted at `/api/v1` prefix in `app/main.py`

Creates an approval decision for a recommendation. Only approved decisions trigger task creation.

**Request:**
```json
{
  "recommendation_id": "uuid",
  "decision": "approve",  // or "reject"
  "rationale": "Connection window critical, expedite approved"
}
```

**Response:**
```json
{
  "case_id": "uuid",
  "recommendation_id": "uuid",
  "decision": "approve",
  "decided_at": "2024-11-23T10:30:00Z",
  "decided_by": "Mariam Al Suwaidi",
  "tasks_created": [
    {
      "task_id": "uuid",
      "case_id": "uuid",
      "status": "assigned",
      "assigned_role": "partner",
      "station_code": "DXB",
      "deadline_utc": "2024-11-23T12:30:00Z",
      "instruction_summary": "Expedite bag transfer to gate B05"
    }
  ]
}
```

**Flow:**
1. Validates case and recommendation exist
2. Records approval decision with approver identity, timestamp, decision code, and rationale
3. If decision is "approve", creates operational tasks via TaskDispatchService
4. If decision is "reject", no tasks created
5. Returns approval decision with list of created tasks (empty for rejected)
6. Creates audit event for approval decision

**Error Cases:**
- 400: Invalid decision code (must be "approve" or "reject")
- 404: Case or recommendation not found
- 409: Returns APPROVAL_REQUIRED if attempting to dispatch tasks before approval (enforced by TaskDispatchService)

## Task Shape

Each generated task includes:

```json
{
  "task_id": "uuid",
  "case_id": "uuid",
  "recommendation_id": "uuid",
  "status": "assigned",  // assigned, acknowledged, in_progress, completed
  "assigned_role": "partner",  // operations or partner
  "assigned_partner_org_code": "DNATA",  // when partner role
  "bag_reference": "EK001234567",
  "station_code": "DXB",
  "flight_context": "EK101 DXB-SYD, departure in 2h6min, gate B05",
  "instructions": "Expedite bag EK001234567 from arrival belt 11 to gate B05 for EK101. Critical connection window.",
  "evidence_links": ["Bag event log", "Transfer scan history", "Flight departure schedule"],
  "deadline": "2024-11-23T12:30:00Z",
  "created_at": "2024-11-23T10:30:00Z",
  "updated_at": "2024-11-23T10:30:00Z"
}
```

## Task Generation Logic

Tasks are generated based on recommendation action code:

- **PRIORITY_TRANSFER**: Creates partner task for bag transfer at DXB
  - Assigned role: partner
  - Partner org: DNATA
  - Instructions: Expedite bag to gate before cutoff
  
- **RESCHEDULE_CONNECTION**: Creates operations task for rebooking
  - Assigned role: operations
  - Instructions: Reschedule passenger and bag to alternative flight
  
- **LOCATE_BAG**: Creates partner task for bag search
  - Assigned role: partner
  - Partner org: DNATA
  - Instructions: Locate bag in transfer area or baggage hold
  
- **MONITOR**: No task created (monitoring only)

## Seed Task IDs and Statuses

The seed data includes these test tasks:

- **TSK-DXB-1187**: Case BC-DXB-240611, bag EK001234567, assigned to DNATA partner, status=assigned
- **TSK-DXB-1189**: Case BC-DXB-240611, bag EK001234568, assigned to DNATA partner, status=assigned
- **TSK-DXB-1181**: Case BC-DXB-240612, bag EK001234569, assigned to DNATA partner, status=acknowledged
- **TSK-DXB-1176**: Case BC-DXB-240614, bag EK001234570, assigned to DNATA partner, status=in_progress

## Approval Decisions in Seed Data

- **Case BC-DXB-240611 (critical)**: Recommendation approved, rationale "Connection window critical, expedite approved"
- **Case BC-DXB-240612 (high)**: Recommendation approved, rationale "Risk justified, approve priority transfer"
- **Case BC-DXB-240611**: Alternative recommendation rejected, rationale "Passive monitoring insufficient"
- **Case BC-DXB-240614 (medium)**: Recommendation approved, rationale "Bag search approved, sufficient buffer time remains"

Some cases have pending recommendations with no approval decision yet, demonstrating the approval requirement workflow.

## Service Layer Components

### ApprovalService
- `record_approval_decision()`: Creates approval decision with validation
- `get_approval_for_recommendation()`: Retrieves latest approval for a recommendation
- `is_approved()`: Checks if recommendation is approved

### TaskDispatchService
- `create_tasks_for_approved_recommendation()`: Generates tasks only for approved recommendations
- Validates approval exists before task creation
- Raises PermissionError (409 conflict) if recommendation not approved
- Atomic commit of tasks with approval verification

### ApprovalRepository
- `get_by_case_and_recommendation()`: Returns latest approval decision
- `create()`: Creates approval with auto-incrementing decision_version
- Enforces unique constraint on (case_id, recommendation_id, decision_version)

### TaskRepository
- `create()`: Creates new task with all required fields
- `list_by_case()`: Returns tasks for a case
- `list_by_status()`: Returns tasks by status with optional role/org filtering
- `update_status()`: Updates task status

## Database Schema

### approval_decisions
- id (PK), case_id (FK), recommendation_id (FK), decided_by_user_id (FK)
- decision_code (approved/rejected), rationale_text, decided_at, decision_version
- Unique constraint on (case_id, recommendation_id, decision_version)

### tasks
- id (PK), case_id (FK), recommendation_id (FK)
- assigned_role_code, assigned_partner_org_code, bag_reference, station_code
- flight_context_text, instruction_text, evidence_links_json
- deadline_at, status_code, created_at, updated_at

## Testing

Comprehensive test coverage in:
- `tests/test_approval_service.py`: 8 tests covering approval recording, validation, versioning
- `tests/test_task_dispatch_service.py`: 6 tests covering task generation, approval enforcement, atomic commit

All tests pass with approval flow validation and 409 conflict enforcement.

## Integration Points

Frontend implementation can:
1. Display recommendations with approval/reject buttons
2. Submit approval decisions to POST /api/v1/operations/cases/{case_id}/approvals
3. Display returned tasks in case detail view
4. Show task status (assigned, acknowledged, in_progress, completed)
5. Partner views filter tasks by assigned_partner_org_code matching user's org

## Acceptance Criteria Met

✓ FR-007: System requires authorized user approval before task dispatch
✓ FR-007: System records approver, decision, and timestamp
✓ FR-007: System prevents autonomous execution without approval (enforced via PermissionError)
✓ FR-008: System creates actionable tasks after approval
✓ FR-008: Each task includes bag reference, deadline, station, flight context, instructions, evidence links
✓ FR-008: System maintains visible relationship between task and parent case
