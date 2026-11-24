/**
 * Executive overview types matching backend API contract
 */

export interface ExecutiveKPI {
  metric_code: string;
  metric_label: string;
  current_value: number;
  trend_direction: 'up' | 'down' | 'flat';
  passenger_impact_note: string | null;
}

export interface ExecutiveTrendData {
  dates: string[];
  exception_rate_per_1000: number[];
  recovered_within_cutoff_pct: number[];
  passengers_impacted: number[];
  open_case_count: number[];
  stale_data_case_count: number[];
}

export interface ExecutiveOverviewResponse {
  from_date: string;
  to_date: string;
  generated_at: string;
  freshness_status: 'fresh' | 'stale' | 'mixed' | 'no_data';
  kpis: ExecutiveKPI[];
  trend_data: ExecutiveTrendData;
}
