/**
 * Passenger-facing baggage and case status types
 */

export interface PassengerMilestone {
  event_type: string;
  observed_at: string;
  source_system: string;
  fact_type: 'observed' | 'derived' | 'estimated';
  freshness_state: 'fresh' | 'stale' | 'awaiting_confirmation';
  location_code: string | null;
}

export interface PassengerBagStatus {
  bag_tag: string;
  latest_confirmed_milestone: string;
  status_label: string;
  estimated_notice: string | null;
  delayed_case_reference: string | null;
  next_expected_update: string | null;
  last_updated_at: string;
  milestones?: PassengerMilestone[];
}

export interface PassengerProgressStep {
  step_text: string;
  status: 'confirmed' | 'estimated';
  timestamp: string | null;
  uncertainty_note: string | null;
}

export interface PassengerCaseStatus {
  case_reference: string;
  progress_state: string;
  latest_confirmed_status: string;
  estimated_notice: string | null;
  next_expected_update: string;
  last_updated_at: string;
  progress_steps?: PassengerProgressStep[];
}
