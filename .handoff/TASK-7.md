# TASK-7 Handoff: Partner Role-Scoped Work Queue and Access Control

## Completion Summary

Implemented partner role-scoped work queue and access control enforcement services covering FR-009 and FR-019.

## Services Implemented

### IdentityAccessService

**Location**: `/repos/emirates_baggage360/backend/app/services/identity_access_service.py`

**Purpose**: Resolves principal identity from JWT and enforces role-based access control

**Key Methods**:
- `resolve_principal(jwt_payload)` - Extracts user context from JWT
- `role_evaluation(principal)` - Returns role code (operations, partner, passenger, executive)
- `permitted_scopes(principal)` - Returns permitted scope list based on role
- `data_filter_rules(principal, operation)` - Returns filter rules for least-privilege data access
- `enforce_partner_org_scope(principal, resource_partner_org)` - Enforces partner org scoping, returns False if 403 should be raised

**Role-Based Filter Rules**:
- **Operations**: Full visibility, no masking, include internal notes and risk scores
- **Partner**: Partner org filter, station filter, mask passenger names, exclude internal notes and risk scores, task-limited visibility
- **Passenger**: Passenger reference filter, exclude internal notes and risk scores, passenger-safe only
- **Executive**: Aggregate only, station filter, mask passenger names, exclude internal notes and risk scores

## Repository Extensions

### TaskRepository Extensions

**Location**: `/repos/emirates_baggage360/backend/app/repositories/task_repository.py`

**New Methods**:

#### `list_by_partner_org_and_role(partner_org_code, assigned_role_code='partner', status_code=None)`

Returns tasks filtered by partner organization. Implements least-privilege query for partner work queue.

**Parameters**:
- `partner_org_code` - Partner organization (e.g., "DNATA", "Menzies")
- `assigned_role_code` - Role code (default: "partner")
- `status_code` - Optional status filter ("assigned", "acknowledged", "in_progress", "completed")

**Returns**: List of Task records ordered by deadline_at ascending

**Example**:
```python
tasks = repo.list_by_partner_org_and_role("DNATA", status_code="assigned")
```

#### `get_by_id_with_partner_scope(task_id, partner_org_code)`

Returns task by ID with partner organization scope enforcement. Returns None if task not found OR if task.assigned_partner_org_code does not match partner_org_code (403 FORBIDDEN_SCOPE).

**Parameters**:
- `task_id` - Task ID
- `partner_org_code` - Current user's partner organization code

**Returns**: Task if found and org matches, None otherwise

**Example**:
```python
task = repo.get_by_id_with_partner_scope(task_id, "DNATA")
if task is None:
    # Return 403 or 404
```

## Schemas

### Partner Schemas

**Location**: `/repos/emirates_baggage360/backend/app/schemas/partner_schemas.py`

#### PartnerTaskCard

Task card for partner work queue display. Excludes internal notes, risk scores, unrelated passenger data.

**Fields**:
- `task_id` - Task UUID
- `case_id` - Case UUID
- `bag_reference` - Bag tag (e.g., "EK001234567")
- `flight_context` - Flight context text
- `station_code` - Station code (e.g., "DXB")
- `deadline_utc` - Task deadline timestamp
- `status` - Task status (assigned, acknowledged, in_progress, completed)
- `instruction_summary` - Brief instruction text

#### PartnerTaskQueueResponse

Partner task queue response matching GET /partner/tasks.

**Shape**:
```json
{
  "items": [PartnerTaskCard, ...],
  "total": 42,
  "generated_at": "2024-11-23T10:30:00Z"
}
```

#### PartnerTaskDetail

Partner task detail with masked passenger data and limited case context. Excludes internal notes and risk scores.

**Fields**:
- `task_id` - Task UUID
- `case_id` - Case UUID
- `case_reference` - Case reference (e.g., "BC-DXB-240611")
- `bag_reference` - Bag tag
- `flight_context` - Flight context text
- `station_code` - Station code
- `deadline_utc` - Task deadline timestamp
- `status` - Task status
- `instructions` - List of instruction strings
- `evidence_links` - List of evidence link strings
- `observed_state_summary` - Limited case context (optional)
- `passenger_name_masked` - Masked passenger name (optional)

## Seed Data

### Partner User

**Email**: `ahmed.hassan@dnata.ae`  
**Password**: `Demo1234!`  
**Role**: `partner`  
**Partner Org**: `DNATA`  
**Station Scope**: `DXB`

### Partner Tasks Assigned to DNATA

#### TSK-DXB-1187
- **Status**: assigned
- **Bag**: EK001234567
- **Flight**: EK101 DXB-SYD, departure in 2h6min, gate B05
- **Instruction**: "Expedite bag EK001234567 from arrival belt 11 to gate B05 for EK101. Critical connection window."
- **Deadline**: Now + 1h36min
- **Case**: BC-DXB-240611 (critical)

#### TSK-DXB-1189
- **Status**: assigned
- **Bag**: EK001234568
- **Flight**: EK101 DXB-SYD, departure in 2h6min, gate B05
- **Instruction**: "Expedite bag EK001234568 from arrival belt 11 to gate B05 for EK101. Critical connection window."
- **Deadline**: Now + 1h36min
- **Case**: BC-DXB-240611 (critical)

#### TSK-DXB-1181
- **Status**: acknowledged
- **Bag**: EK001234569
- **Flight**: EK103 DXB-SIN, departure in 2h55min, gate C10
- **Instruction**: "Expedite bag EK001234569 to gate C10 for EK103."
- **Deadline**: Now + 2h25min
- **Case**: BC-DXB-240612 (high)

#### TSK-DXB-1176
- **Status**: in_progress
- **Bag**: EK001234570
- **Flight**: EK105 DXB-BKK, departure in 3h15min, gate D08
- **Instruction**: "Locate bag EK001234570 in transfer area. Confirm current location and status."
- **Deadline**: Now + 2h45min

## API Endpoints - NOT IMPLEMENTED IN THIS TASK

**IMPORTANT**: This task implements only the service layer (IdentityAccessService), repository layer (TaskRepository extensions), and schemas (partner_schemas.py). The API endpoints themselves are NOT part of this task and will be implemented in a future backend API task.

The OpenAPI specification defines partner task endpoints, but they are not yet mounted in the FastAPI application. A future task will create the partner router and mount these endpoints.

### Future Endpoint: Partner Task Queue

Will be implemented as: `GET` with path `/api/v1/partner/tasks`

Query parameter: `status` (optional) - Filter by status

Expected response shape: PartnerTaskQueueResponse with `items`, `total`, `generated_at`

### Future Endpoint: Partner Task Detail

Will be implemented as: `GET` with path `/api/v1/partner/tasks/{task_id}`

Path parameter: `task_id` - Task UUID

Expected response shape: PartnerTaskDetail with task fields, limited case context, masked passenger data

Expected 403 enforcement: Return 403 FORBIDDEN_SCOPE if task org does not match user org

## 403 FORBIDDEN_SCOPE Enforcement

Partner users receive 403 FORBIDDEN_SCOPE when:
1. Attempting to access a task assigned to a different partner organization
2. Attempting to access endpoints outside their permitted scopes

**Implementation**:
- `TaskRepository.get_by_id_with_partner_scope()` returns None when org mismatch
- Route handler should check for None and return 403 response
- `IdentityAccessService.enforce_partner_org_scope()` returns False when org mismatch

**Example Route Pattern** (future task):
```python
@router.get("/partner/tasks/{task_id}")
def get_partner_task_detail(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = TaskRepository(db)
    task = repo.get_by_id_with_partner_scope(task_id, current_user.partner_org_code)
    
    if task is None:
        raise HTTPException(status_code=403, detail="FORBIDDEN_SCOPE")
    
    # Build PartnerTaskDetail response with masked data
    return PartnerTaskDetail(...)
```

## Test Coverage

### test_identity_access_service.py

Tests covering:
- Principal resolution from JWT
- Role evaluation
- Permitted scopes for all roles (operations, partner, passenger, executive)
- Data filter rules for all roles
- Partner org scope enforcement (allow/deny)
- 403 enforcement when partner org mismatch

### test_partner_integration.py

Tests covering:
- `list_by_partner_org_and_role` filtering by partner org
- `list_by_partner_org_and_role` filtering by status
- `get_by_id_with_partner_scope` allowing matching org
- `get_by_id_with_partner_scope` denying different org (returns None for 403)

## Verification Commands

```bash
cd /repos/emirates_baggage360/backend
.venv/bin/python -m pytest tests/test_identity_access_service.py tests/test_partner_integration.py -v
.venv/bin/python -m ruff check app/services/identity_access_service.py app/schemas/partner_schemas.py
.venv/bin/python -m mypy app/services/identity_access_service.py app/schemas/partner_schemas.py --ignore-missing-imports
```

## Next Steps

A future frontend task will implement:
- Partner task queue page component
- Partner task detail page component
- API client methods for GET /partner/tasks and GET /partner/tasks/{task_id}
- Partner-scoped navigation header (no sidebar)
- Deadline emphasis and scoping notice UI
