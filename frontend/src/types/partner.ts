/**
 * Partner-scoped types for task queue and task detail screens.
 * Matches backend partner_schemas.py definitions.
 */

export interface PartnerTaskCard {
  task_id: string;
  case_id: string;
  bag_reference: string;
  flight_context: string;
  station_code: string;
  deadline_utc: string;
  status: 'assigned' | 'acknowledged' | 'in_progress' | 'completed';
  instruction_summary: string;
}

export interface PartnerTaskQueueResponse {
  items: PartnerTaskCard[];
  total: number;
  generated_at: string;
}

export interface PartnerTaskDetail {
  task_id: string;
  case_id: string;
  case_reference: string;
  bag_reference: string;
  flight_context: string;
  station_code: string;
  deadline_utc: string;
  status: 'assigned' | 'acknowledged' | 'in_progress' | 'completed';
  instructions: string[];
  evidence_links: string[];
  observed_state_summary?: string;
  passenger_name_masked?: string;
}

export interface TaskEventRequest {
  event_type: 'acknowledged' | 'in_progress' | 'completed';
  client_event_id: string;
  note?: string;
  evidence_type?: 'scan_confirmation' | 'handover_proof' | 'completion_note';
  evidence_reference?: string;
}

export interface TaskEventResponse {
  task_id: string;
  event_type: string;
  recorded_at: string;
  case_status: string;
}

export interface TaskEvidence {
  task_evidence_id: string;
  event_type: string;
  recorded_at: string;
  actor_display: string;
  evidence_summary: string;
}
