/**
 * Operations types for cockpit, case detail, and operations workflows
 */

export interface BagMilestone {
  event_type: string;
  observed_at: string;
  source_system: string;
  fact_type: 'observed' | 'derived' | 'estimated';
  freshness_state: 'fresh' | 'stale' | 'awaiting_confirmation';
  location_code: string | null;
}

export interface JourneyContext {
  journey_id: string;
  inbound_flight: string;
  onward_flight: string;
  connection_window_minutes: number;
  gate_change: string | null;
  stand_change: string | null;
  aircraft_change: string | null;
}

export interface BagTimeline {
  bag_id: string;
  bag_tag: string;
  passenger_name_masked: string;
  journey_context: JourneyContext | null;
  milestones: BagMilestone[];
}

export interface ExceptionCase {
  case_id: string;
  case_reference: string;
  exception_type: string;
  severity_code: 'critical' | 'high' | 'medium' | 'low';
  deadline_at: string;
  status_code: string;
  observed_state_summary: string;
  predicted_state_summary: string;
  bag_count: number;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
}

export interface Recommendation {
  recommendation_id: string;
  case_id: string;
  action_code: string;
  action_label: string;
  reason_text: string;
  confidence_score: number;
  freshness_state: 'fresh' | 'stale' | 'awaiting_confirmation';
  evidence: string[];
  generated_at: string;
  superseded_at: string | null;
}

export interface KPIMetric {
  label: string;
  value: number;
  note: string;
  urgent?: boolean;
}

export interface CaseRow {
  severity: 'critical' | 'high' | 'medium' | 'low';
  case_ref: string;
  flight_dest: string;
  time_to_cutoff: string;
  bags: number;
  pax_impact: string;
  reason: string;
  freshness: string;
  owner: string;
}

export interface TaskSummary {
  task_id: string;
  case_id: string;
  status: string;
  assigned_role: string;
  station_code: string;
  deadline_utc: string;
  instruction_summary: string;
}

export interface ApprovalDecisionRequest {
  recommendation_id: string;
  decision: 'approve' | 'reject';
  rationale: string;
}

export interface ApprovalDecisionResponse {
  case_id: string;
  recommendation_id: string;
  decision: 'approve' | 'reject';
  decided_at: string;
  decided_by: string;
  tasks_created: TaskSummary[];
}

export interface AuditEvent {
  audit_event_id: string;
  actor_user_id: string;
  action_type: string;
  entity_type: string;
  entity_id: string;
  correlation_id: string;
  outcome_code: string;
  detail: Record<string, unknown>;
  occurred_at: string;
}
