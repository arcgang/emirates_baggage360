# TASK-12 Handoff: UI U2 - Partner Screens

## Completion Summary

Implemented partner task queue and task detail pages with partner router integration, covering FR-009 and FR-010 UI requirements.

## Frontend Components Implemented

### TaskQueuePage.tsx
**Location**: `/repos/emirates_baggage360/frontend/src/pages/partner/TaskQueuePage.tsx`

**Purpose**: Partner work queue with status filtering, deadline emphasis, and role scoping notice

**Features**:
- Status tabs: assigned, acknowledged, in_progress, completed with counts
- Task table with deadline emphasis (overdue, critical, warning)
- Refresh button with last-updated timestamp
- Scoping banner: "You see only tasks assigned to your role"
- Empty queue and loading states
- 403 role-scope error handling

### TaskDetailPage.tsx
**Location**: `/repos/emirates_baggage360/frontend/src/pages/partner/TaskDetailPage.tsx`

**Purpose**: Task detail with acknowledgement and evidence submission

**Features**:
- Task header with ID, bag reference, deadline countdown
- "Your view of the case" section with flight context, station, case reference
- "Hidden from your role" notice (passenger name, risk scores, internal notes masked)
- Instructions section with numbered steps
- Acknowledge button for assigned tasks
- Evidence submission form
- Evidence history table
- 403/404 error handling with user-friendly messages

### TaskTable.tsx
**Location**: `/repos/emirates_baggage360/frontend/src/components/partner/TaskTable.tsx`

**Purpose**: Reusable task table component with deadline emphasis

**Features**:
- Table columns: Task ID, Bag reference, Flight context, Station, Deadline, Status, Instruction summary, Action
- Deadline emphasis: overdue (red + alert icon), critical (<30min, red), warning (30-60min), normal
- Status chips: assigned (blue), acknowledged (green), in_progress (yellow), completed (green)
- First row highlighting (pink background, red left border, primary action button)
- Empty and loading states

### TaskHeader.tsx
**Location**: `/repos/emirates_baggage360/frontend/src/components/partner/TaskHeader.tsx`

**Purpose**: Task metadata and deadline display

**Features**:
- Task ID as page heading
- Bag reference display
- Deadline countdown with emphasis (overdue, critical, warning, normal)
- Status chip display

### EvidenceForm.tsx
**Location**: `/repos/emirates_baggage360/frontend/src/components/partner/EvidenceForm.tsx`

**Purpose**: Evidence submission with client event ID generation

**Features**:
- Evidence type select (scan_confirmation, handover_proof, completion_note)
- Evidence reference input
- Note textarea
- Client event ID generation (`CLIENT-EVT-{timestamp}-{random}`)
- Submit button with loading state
- Form validation

## Backend Router Implemented

### PartnerRouter
**Location**: `/repos/emirates_baggage360/backend/app/routers/partner.py`

**Purpose**: Partner API endpoints for task queue and detail

**Endpoints**:
- `GET /api/v1/partner/tasks` - Partner task queue with optional status filter
- `GET /api/v1/partner/tasks/{task_id}` - Partner task detail with 403 enforcement
- `POST /api/v1/partner/tasks/{task_id}/events` - Task event submission

**Task Reference Formatting**:
- Converts UUID task IDs to friendly format: TSK-{STATION}-{NUMBER}
- Example: `00000000-0000-0000-0000-0000000004a3` → `TSK-DXB-1187`
- Accepts both UUID and TSK- format in URLs

**403 Enforcement**:
- Verifies partner user authentication
- Enforces partner organization scoping via TaskRepository.get_by_id_with_partner_scope()
- Returns 403 FORBIDDEN_SCOPE when task org mismatches user org

**Mounted in**: `/repos/emirates_baggage360/backend/app/main.py`

## Types

### partner.ts
**Location**: `/repos/emirates_baggage360/frontend/src/types/partner.ts`

**Types**:
- `PartnerTaskCard` - Task queue item
- `PartnerTaskQueueResponse` - Task queue response with items, total, generated_at
- `PartnerTaskDetail` - Task detail with masked data
- `TaskEventRequest` - Event submission request
- `TaskEventResponse` - Event submission response
- `TaskEvidence` - Evidence history item

## Wireframe Compliance

### wireframe_partner_task_queue.html
Implemented:
- ✓ Top nav with Baggage360 logo, "My tasks" link, SIMULATED badge, role chip, time, sign out
- ✓ Page heading "My tasks" with station, last updated timestamp, freshness badge
- ✓ Refresh button
- ✓ Scoping notice banner with eye icon
- ✓ Status tabs with counts
- ✓ Task table with 8 columns
- ✓ Deadline emphasis (overdue red + alert, critical red + clock, warning yellow + clock)
- ✓ Status chips with icons
- ✓ Primary action styling on first row
- ✓ Empty queue state
- ✓ Loading state
- ✓ Role-scope error (403) banner

### wireframe_partner_task_detail.html
Implemented:
- ✓ Top nav (same as queue page)
- ✓ Breadcrumb navigation
- ✓ Task header with ID, bag reference, deadline countdown, status chip
- ✓ "Your view of the case" section with bag reference, flight context, station, case reference
- ✓ "Hidden from your role" notice with eye icon and bulleted list
- ✓ Instructions section with numbered steps
- ✓ Acknowledge button (for assigned tasks)
- ✓ Evidence form with select, input, textarea
- ✓ Evidence history table
- ✓ 403/404 error states

## E2E Tests

### wireframe_04_partner_task_queue.spec.ts
**Location**: `/repos/emirates_baggage360/frontend/e2e/wireframe_04_partner_task_queue.spec.ts`

**Coverage**:
- Logs in with ahmed.hassan@dnata.ae / Demo1234!
- Verifies tasks TSK-DXB-1187 and TSK-DXB-1189 appear in assigned tab
- Verifies deadline emphasis on first task
- Verifies status tab counts

**Status**: ✓ PASSED

### wireframe_05_partner_task_detail.spec.ts
**Location**: `/repos/emirates_baggage360/frontend/e2e/wireframe_05_partner_task_detail.spec.ts`

**Coverage**:
- Logs in with ahmed.hassan@dnata.ae / Demo1234!
- Opens task TSK-DXB-1187
- Submits acknowledgement (if status is assigned)
- Submits evidence with scan confirmation
- Verifies breadcrumb navigation

**Status**: ✓ PASSED

## Seed Data Used

### Partner User
- Email: ahmed.hassan@dnata.ae
- Password: Demo1234!
- Role: partner
- Partner Org: DNATA
- Station: DXB

### Partner Tasks
- TSK-DXB-1187 (UUID 1187): assigned, bag EK001234567, case BC-DXB-240611, deadline +1h36min
- TSK-DXB-1189 (UUID 1189): assigned, bag EK001234568, case BC-DXB-240611, deadline +1h36min
- TSK-DXB-1181 (UUID 1181): acknowledged, bag EK001234569, case BC-DXB-240612, deadline +2h25min
- TSK-DXB-1176 (UUID 1176): in_progress, bag EK001234570, case BC-DXB-240613, deadline +2h45min

## Verification

```bash
cd /repos/emirates_baggage360/frontend
npm run build
npx vitest run src/__tests__/pages/TaskQueuePage.test.tsx src/__tests__/pages/TaskDetailPage.test.tsx
npx playwright test e2e/wireframe_04_partner_task_queue.spec.ts
npx playwright test e2e/wireframe_05_partner_task_detail.spec.ts
```

## Cross-Page Consistency

Partner screens maintain consistent styling with operations screens:
- Same header structure and navigation pattern
- Same card, button, chip, and banner styles
- Same deadline emphasis colors and icons (red for critical/overdue, yellow for warning)
- Same loading and empty states
- Same error handling pattern (403, 404)

## Scope Extension

Extended scope to implement partner router (`/repos/emirates_baggage360/backend/app/routers/partner.py`) and mount it in `main.py` because:
1. Contract checker requires backend routes for frontend API calls
2. E2E tests require live backend endpoints
3. Backend tasks 7 and 8 implemented only service/repository/schema layers without routes
4. Without router, frontend screens would fail all E2E tests with 404 errors

Task reference formatting was added to partner router to convert UUIDs to user-friendly task IDs (TSK-DXB-1187) matching wireframe design.

## Next Steps

Partner screens are complete and ready for integration. Future enhancements may include:
- Real-time task updates via WebSocket
- Bulk acknowledgement for multiple tasks
- Evidence file upload
- Task search and filtering by bag/flight/deadline
