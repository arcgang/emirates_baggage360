# Graph Report - emirates_baggage360  (2026-11-23)

## Corpus Check
- 158 files · ~96,497 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: (none) 6, .bat 2, .ini 1)

## Summary
- 1521 nodes · 3185 edges · 94 communities (59 shown, 35 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 346 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fd7a7bed`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Emirates Baggage360
- seed.py
- datetime
- test_approval_service.py
- auth.py
- uuid
- conftest.py
- TASK-3 Handoff: Bag Journey Visibility and Context Correlation
- devDependencies
- CaseDetailPage.tsx
- compilerOptions
- auth.ts
- baggage360-backend
- test_pipeline_migration_parity.py
- test_identity_access_service.py
- TASK-7 Handoff: Partner Role-Scoped Work Queue and Access Control
- TASK-4 Handoff: Source Freshness and Connection Risk
- BagEvent
- get_partner_tasks
- TASK-5 Handoff: Backend Feature B3 - Exception Grouping and Recommendations
- ExceptionCaseService
- sqlalchemy_orm
- AuditService
- react
- operations_schemas.py
- test_passenger_status_service.py
- steps
- TASK-12 Handoff: UI U2 - Partner Screens
- ExceptionCase
- TASK-8 Handoff: Backend Feature B6 - Task Acknowledgement and Passenger Bag Status
- Task
- pytest
- test_executive_overview_service.py
- TASK-6 Handoff: Approval and Task Dispatch
- TASK-10 Handoff: Backend Feature B8 - Case Audit Trail and Executive Overview
- uuid
- db_session
- correlation_id.py
- get_operations_case_detail
- env.py
- TaskEvidence
- test_smoke.py
- TaskQueuePage.tsx
- json
- OverviewPage.tsx
- executive.py
- bag_journey_service.py
- utils.ts
- AuditRepository
- BagEvent
- TASK-9 Handoff: Passenger Delayed-Bag Case Status
- eslint.config.js
- App.tsx
- @playwright/test
- scripts
- TaskDetailPage.tsx
- vite
- package.json
- useAuth
- environment
- main.py
- environment
- Audit Event Shape
- api-client.ts
- config.py
- get_db
- .get_audit_trail_for_case
- start.sh
- Integration Notes
- docker-entrypoint.sh
- stop.sh

## God Nodes (most connected - your core abstractions)
1. `ExceptionCase` - 80 edges
2. `User` - 58 edges
3. `Bag` - 53 edges
4. `BagEvent` - 48 edges
5. `PassengerJourney` - 47 edges
6. `Recommendation` - 45 edges
7. `Task` - 40 edges
8. `JourneyLeg` - 39 edges
9. `ExceptionCaseRepository` - 32 edges
10. `get_operations_case_detail()` - 32 edges

## Surprising Connections (you probably didn't know these)
- `Next Steps for Frontend` --references--> `BagTimeline`  [INFERRED]
  .handoff/TASK-3.md → backend/app/schemas/operations_schemas.py
- `Expected Integration Pattern (for future implementation)` --references--> `PassengerCaseStatus`  [INFERRED]
  .handoff/TASK-9.md → backend/app/schemas/passenger_schemas.py
- `For Future API Task` --references--> `ExecutiveOverviewResponse`  [INFERRED]
  .handoff/TASK-10.md → backend/app/schemas/executive_schemas.py
- `For Audit Trail Integration` --references--> `AuditService`  [INFERRED]
  .handoff/TASK-10.md → backend/app/services/audit_service.py
- `PassengerStatusService Extensions` --references--> `PassengerCaseView`  [INFERRED]
  .handoff/TASK-9.md → backend/app/models/passenger_view.py

## Import Cycles
- None detected.

## Communities (94 total, 35 thin omitted)

### Community 0 - "Emirates Baggage360"
Cohesion: 0.07
Nodes (29): API Documentation, Architecture, Backend, Backend, Backend Configuration, Backend Tests, CI/CD, Configuration (+21 more)

### Community 1 - "seed.py"
Cohesion: 0.10
Nodes (15): SessionAccessLog, hash_password(), run_seed(), seed_approval_decisions(), seed_bags(), seed_case_bags(), seed_exception_cases(), seed_executive_metrics() (+7 more)

### Community 3 - "test_approval_service.py"
Cohesion: 0.14
Nodes (9): ApprovalService, test_decision_version_increment(), test_is_approved(), test_record_approval_approved(), test_record_approval_case_not_found(), test_record_approval_invalid_decision_code(), test_record_approval_recommendation_not_found(), test_record_approval_rejected() (+1 more)

### Community 4 - "auth.py"
Cohesion: 0.16
Nodes (6): get_current_principal(), login(), LoginRequest, LoginResponse, logout(), PrincipalContext

### Community 5 - "uuid"
Cohesion: 0.14
Nodes (9): Bag, CaseBag, RecommendationService, test_generate_recommendations_calculates_freshness_state(), test_generate_recommendations_creates_priority_transfer_for_critical_case(), test_generate_recommendations_includes_confidence_scores(), test_generate_recommendations_includes_evidence_json(), test_generate_recommendations_includes_reason_text() (+1 more)

### Community 6 - "conftest.py"
Cohesion: 0.14
Nodes (5): auth_client(), client(), override_get_db(), db_session(), _fresh_schema()

### Community 7 - "TASK-3 Handoff: Bag Journey Visibility and Context Correlation"
Cohesion: 0.09
Nodes (22): BagEventRepository, BagJourneyService, BagMilestone Schema, BagRepository, BagTimeline Schema, Data Models Created, Fact Type Semantics, Freshness Calculation Logic (+14 more)

### Community 8 - "devDependencies"
Cohesion: 0.12
Nodes (16): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @playwright/test@^1.49.1, tailwindcss@^3.4.15, @testing-library/jest-dom@^6.6.3, @testing-library/react@^16.0.1, @testing-library/user-event@^14.5.2 (+8 more)

### Community 9 - "CaseDetailPage.tsx"
Cohesion: 0.10
Nodes (29): ApprovalForm(), ApprovalFormProps, BagTimeline(), BagTimelineProps, getFactTypeColor(), getFreshnessColor(), CaseHeader(), CaseHeaderProps (+21 more)

### Community 10 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+11 more)

### Community 11 - "auth.ts"
Cohesion: 0.25
Nodes (5): LoginRequest, LoginResponse, PrincipalContext, ErrorResponse, PaginatedResponse

### Community 20 - "test_pipeline_migration_parity.py"
Cohesion: 0.18
Nodes (12): _alembic(), _annotation_kind(), _column_kind(), _env_py_text(), _foreign_key(), _has_alembic_version(), _last_name(), _mapped_columns() (+4 more)

### Community 21 - "test_identity_access_service.py"
Cohesion: 0.06
Nodes (16): IdentityAccessService, service(), test_data_filter_rules_for_operations(), test_data_filter_rules_for_partner(), test_data_filter_rules_for_passenger(), test_enforce_partner_org_scope_allows_matching_org(), test_enforce_partner_org_scope_allows_non_partner_roles(), test_enforce_partner_org_scope_denies_different_org() (+8 more)

### Community 22 - "TASK-7 Handoff: Partner Role-Scoped Work Queue and Access Control"
Cohesion: 0.07
Nodes (28): API Endpoints - NOT IMPLEMENTED IN THIS TASK, Completion Summary, Future Endpoint: Partner Task Detail, Future Endpoint: Partner Task Queue, `get_by_id_with_partner_scope(task_id, partner_org_code)`, IdentityAccessService, `list_by_partner_org_and_role(partner_org_code, assigned_role_code='partner', status_code=None)`, Next Steps (+20 more)

### Community 23 - "TASK-4 Handoff: Source Freshness and Connection Risk"
Cohesion: 0.11
Nodes (17): 1. RiskAssessmentService (`backend/app/services/risk_assessment_service.py`), 2. BagEventRepository Freshness Calculation (`backend/app/repositories/bag_repository.py`), 3. Extended Schemas (`backend/app/schemas/operations_schemas.py`), 4. Extended Seed Data (`backend/app/seed.py`), Acceptance Criteria Coverage, Database Schema (No Changes), For Bag Timeline (Already Implemented in TASK-3):, For Operations Cockpit (Future Task): (+9 more)

### Community 24 - "BagEvent"
Cohesion: 0.11
Nodes (10): JourneyLeg, PassengerJourney, RiskAssessmentService, test_calculate_connection_risk_critical(), test_calculate_connection_risk_late_inbound(), test_calculate_connection_risk_moderate(), test_evaluate_risk_integration(), test_freshness_calculation() (+2 more)

### Community 25 - "get_partner_tasks"
Cohesion: 0.20
Nodes (5): format_task_reference(), get_current_partner_user(), get_partner_task_detail(), get_partner_tasks(), PartnerTaskQueueResponse

### Community 26 - "TASK-5 Handoff: Backend Feature B3 - Exception Grouping and Recommendations"
Cohesion: 0.07
Nodes (26): BC-DXB-240611 (Critical, 3 bags), BC-DXB-240612 (High, 2 bags), BC-DXB-240613 (High, 2 bags), BC-DXB-240614 (Medium, 1 bag), Confidence Ranges, Data Shapes, Depends On, ExceptionCase Schema (+18 more)

### Community 27 - "ExceptionCaseService"
Cohesion: 0.17
Nodes (3): ExceptionCaseService, test_create_case_calculates_deadline_from_onward_flight(), test_create_case_groups_bags_with_severity()

### Community 28 - "sqlalchemy_orm"
Cohesion: 0.06
Nodes (4): ApprovalRepository, ExceptionCaseRepository, RecommendationRepository, test_get_case_bag_count()

### Community 29 - "AuditService"
Cohesion: 0.17
Nodes (7): AuditService, test_audit_event_detail_json_parsing(), test_correlation_id_propagation(), test_get_audit_trail_for_case(), test_record_audit_event(), test_record_audit_event_nullable_actor(), test_trace_by_correlation_id()

### Community 30 - "react"
Cohesion: 0.25
Nodes (9): BagJourney(), BagJourneyProps, Milestone, MilestoneList(), MilestoneListProps, StatusHeadline(), StatusHeadlineProps, BagStatusPage() (+1 more)

### Community 31 - "operations_schemas.py"
Cohesion: 0.10
Nodes (15): get_operations_cockpit(), post_case_approval(), ApprovalDecisionRequest, ApprovalDecisionResponse, AuditEvent, CockpitCaseCard, CockpitSummary, ExceptionCase (+7 more)

### Community 32 - "test_passenger_status_service.py"
Cohesion: 0.05
Nodes (21): PassengerCaseView, PassengerViewRepository, get_passenger_bag_status(), get_passenger_case_status(), PassengerBagStatus, PassengerCaseStatus, PassengerMilestone, PassengerProgressStep (+13 more)

### Community 33 - "steps"
Cohesion: 0.06
Nodes (38): name, runs-on, services, steps, DATABASE_URL, JWT_SECRET_KEY, POSTGRES_DB, POSTGRES_PASSWORD (+30 more)

### Community 34 - "TASK-12 Handoff: UI U2 - Partner Screens"
Cohesion: 0.08
Nodes (25): Backend Router Implemented, Completion Summary, Cross-Page Consistency, E2E Tests, EvidenceForm.tsx, Frontend Components Implemented, Next Steps, Partner Tasks (+17 more)

### Community 35 - "ExceptionCase"
Cohesion: 0.06
Nodes (18): ExceptionCase, Recommendation, User, test_data(), test_list_prioritized_cases_filters_by_severity(), test_list_prioritized_cases_orders_by_deadline(), test_update_case_status(), test_post_case_approval_with_approve_decision() (+10 more)

### Community 36 - "TASK-8 Handoff: Backend Feature B6 - Task Acknowledgement and Passenger Bag Status"
Cohesion: 0.06
Nodes (27): PartnerTaskCard, PartnerTaskDetail, TaskEventRequest, TaskEventResponse, Completed Services, Future Integration Notes, Implementation Summary, Partner Schemas (partner_schemas.py) (+19 more)

### Community 37 - "Task"
Cohesion: 0.09
Nodes (10): Task, TaskRepository, post_partner_task_event(), TaskDispatchService, test_accept_task_event_acknowledged(), test_accept_task_event_all_tasks_completed_closes_case(), test_accept_task_event_completed_updates_case(), test_accept_task_event_idempotent_replay() (+2 more)

### Community 39 - "pytest"
Cohesion: 0.27
Nodes (6): _env(), _is_async(), _run(), _seed_module(), seeded(), test_the_seed_runs_a_second_time()

### Community 40 - "test_executive_overview_service.py"
Cohesion: 0.06
Nodes (19): ExecutiveDailyMetric, ExecutiveMetricsRepository, ExecutiveOverviewService, test_get_executive_overview_aggregates_multiple_stations(), test_get_executive_overview_freshness_status(), test_get_executive_overview_kpis_structure(), test_get_executive_overview_trend_data(), test_get_executive_overview_with_date_range() (+11 more)

### Community 42 - "TASK-6 Handoff: Approval and Task Dispatch"
Cohesion: 0.10
Nodes (18): Acceptance Criteria Met, approval_decisions, Approval Decisions in Seed Data, Approval Flow, ApprovalRepository, Completed Implementation, Database Schema, Integration Points (+10 more)

### Community 43 - "TASK-10 Handoff: Backend Feature B8 - Case Audit Trail and Executive Overview"
Cohesion: 0.12
Nodes (15): Acceptance Criteria Coverage, API Endpoints, Audit Events, Completion Summary, Created, Executive Daily Metrics, Files Created/Modified, Modified (+7 more)

### Community 44 - "uuid"
Cohesion: 0.11
Nodes (13): BagJourneyService, test_bag_at_risk(), test_bag_not_found(), test_bag_on_time(), test_compose_bag_timeline_at_risk(), test_compose_bag_timeline_on_time(), test_events_at_risk(), test_events_on_time() (+5 more)

### Community 47 - "get_operations_case_detail"
Cohesion: 0.14
Nodes (3): JourneyRepository, get_operations_case_detail(), JourneyContext

### Community 48 - "env.py"
Cohesion: 0.27
Nodes (3): get_url(), run_migrations_offline(), run_migrations_online()

### Community 50 - "test_smoke.py"
Cohesion: 0.25
Nodes (3): test_database_session(), test_get_current_principal(), test_health_check()

### Community 51 - "TaskQueuePage.tsx"
Cohesion: 0.21
Nodes (6): TaskTable(), TaskTableProps, formatRelativeTime(), StatusFilter, TaskQueuePage(), PartnerTaskCard

### Community 52 - "json"
Cohesion: 0.21
Nodes (5): seed_bag_events(), test_get_passenger_bag_status_excludes_internal_notes(), test_get_passenger_bag_status_with_confirmed_and_estimated_separation(), test_get_passenger_bag_status_with_passenger_safe_filtering(), test_get_passenger_case_status_with_progress_stepper()

### Community 54 - "OverviewPage.tsx"
Cohesion: 0.17
Nodes (16): CategoryBreakdown(), CategoryBreakdownProps, CategoryData, formatKPIValue(), getKPIDescription(), getTrendColor(), getTrendText(), KPICards() (+8 more)

### Community 55 - "executive.py"
Cohesion: 0.14
Nodes (7): get_executive_overview(), ExecutiveKPI, ExecutiveOverviewResponse, ExecutiveTrendData, ExecutiveSchemas, Extended OperationsSchemas, Schema Layer Implemented

### Community 58 - "utils.ts"
Cohesion: 0.22
Nodes (9): dependencies, clsx@^2.1.1, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, tailwind-merge@^2.5.5, clsx, react-dom (+1 more)

### Community 59 - "AuditRepository"
Cohesion: 0.11
Nodes (4): AuditEvent, AuditRepository, seed_audit_events(), AuditRepository

### Community 60 - "BagEvent"
Cohesion: 0.10
Nodes (3): BagEvent, BagEventRepository, BagRepository

### Community 61 - "TASK-9 Handoff: Passenger Delayed-Bag Case Status"
Cohesion: 0.10
Nodes (20): Excludes (never exposed to passengers):, Expected Integration Pattern (for future implementation), FR-013: Separation of confirmed vs estimated passenger information, FR-014: Delayed-bag case status and next steps, FR Acceptance Coverage, Includes (passenger-safe):, Integration Notes for Future Tasks, No API Endpoint Added (+12 more)

### Community 62 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@^10.0.1, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^17.14.0, typescript-eslint@^8.74.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 63 - "App.tsx"
Cohesion: 0.17
Nodes (15): App(), RequireAuth(), RequireAuthProps, AuthContext, AuthContextType, AuthProvider(), LoginCredentials, LoginResponse (+7 more)

### Community 67 - "scripts"
Cohesion: 0.29
Nodes (7): scripts, build, dev, lint, preview, test, type-check

### Community 68 - "TaskDetailPage.tsx"
Cohesion: 0.27
Nodes (10): EvidenceForm(), EvidenceFormProps, TaskHeader(), TaskHeaderProps, TaskDetailPage(), PartnerTaskDetail, PartnerTaskQueueResponse, TaskEventRequest (+2 more)

### Community 69 - "vite"
Cohesion: 0.40
Nodes (4): vite@^6.0.1, @vitejs/plugin-react@^4.3.4, vite, @vitejs/plugin-react

### Community 70 - "package.json"
Cohesion: 0.15
Nodes (12): jsdom@^25.0.1, postcss@^8.4.49, @types/react@^18.3.12, typescript@^5.6.3, name, private, type, version (+4 more)

### Community 71 - "useAuth"
Cohesion: 0.27
Nodes (8): Header(), Layout(), LayoutProps, NavItem, navItems, Sidebar(), TopNav(), cn()

### Community 72 - "environment"
Cohesion: 0.08
Nodes (24): PIP_TARGET, build, depends_on, environment, args, context, environment, image (+16 more)

### Community 74 - "environment"
Cohesion: 0.10
Nodes (21): build, environment, ports, volumes, x-preview-port, context, CORS_ORIGINS, DATABASE_URL (+13 more)

### Community 75 - "Audit Event Shape"
Cohesion: 0.50
Nodes (4): Action Types, Audit Event Shape, Entity Types, Fields

### Community 76 - "api-client.ts"
Cohesion: 0.17
Nodes (10): vitest@^2.1.5, apiClient, ApiError, request(), CaseStatusPage(), PassengerBagStatus, PassengerCaseStatus, PassengerMilestone (+2 more)

### Community 82 - ".get_audit_trail_for_case"
Cohesion: 0.33
Nodes (4): AuditService, CorrelationIdMiddleware, ExecutiveOverviewService, Service Layer Implemented

### Community 83 - "start.sh"
Cohesion: 0.48
Nodes (6): check_prerequisites(), DATABASE_URL, find_available_port(), native_path(), port_in_use(), start.sh script

### Community 84 - "Integration Notes"
Cohesion: 0.50
Nodes (4): Correlation ID Middleware Integration, For Audit Trail Integration, For Future API Task, Integration Notes

## Knowledge Gaps
- **2 isolated node(s):** `baggage360-backend`, `DATABASE_URL`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 739 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `ExceptionCase` to `test_passenger_status_service.py`, `seed.py`, `datetime`, `test_approval_service.py`, `auth.py`, `uuid`, `Task`, `test_executive_overview_service.py`, `get_operations_case_detail`, `test_smoke.py`, `json`, `ExceptionCaseService`, `sqlalchemy_orm`, `operations_schemas.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `ExceptionCase` (e.g. with `ApprovalDecision` and `Recommendation`) actually correct?**
  _`ExceptionCase` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `baggage360-backend`, `DATABASE_URL` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Emirates Baggage360` be split into smaller, more focused modules?**
  _Cohesion score 0.06666666666666667 - nodes in this community are weakly interconnected._
- **Why does `ExceptionCase` connect `ExceptionCase` to `test_passenger_status_service.py`, `seed.py`, `datetime`, `test_approval_service.py`, `Task`, `uuid`, `.get_by_reference`, `test_executive_overview_service.py`, `get_operations_case_detail`, `json`, `BagEvent`, `ExceptionCaseService`, `sqlalchemy_orm`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `User` (e.g. with `get_operations_case_detail()` and `post_case_approval()`) actually correct?**
  _`User` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `seed.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._