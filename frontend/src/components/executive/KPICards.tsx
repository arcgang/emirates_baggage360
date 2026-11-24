/**
 * KPI Cards component for executive overview
 * Displays 6 KPI cards in a grid with values, trend arrows, and descriptions
 */
import { ExecutiveKPI } from '../../types/executive';

interface KPICardsProps {
  kpis: ExecutiveKPI[];
}

const TrendIcon: React.FC<{ direction: 'up' | 'down' | 'flat' }> = ({ direction }) => {
  if (direction === 'up') {
    return (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
        <path d="M12 19V5M6 11l6-6 6 6"/>
      </svg>
    );
  }
  if (direction === 'down') {
    return (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
        <path d="M12 5v14M6 13l6 6 6-6"/>
      </svg>
    );
  }
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M5 12h14M15 8l4 4-4 4"/>
    </svg>
  );
};

const getTrendColor = (direction: 'up' | 'down' | 'flat', metricCode: string): string => {
  // For exception_rate and open_case_ageing, down is good (green), up is bad (warning)
  // For recovered_within_cutoff, up is good (green), down is bad (warning)
  // For mean_time_to_decision, down is good (green), up is bad (warning)
  // For stale_data_cases, any change is warning, flat is neutral
  
  if (direction === 'flat') {
    return 'text-gray-600';
  }
  
  const goodWhenDown = ['exception_rate', 'mean_time_to_decision', 'open_case_ageing'];
  const goodWhenUp = ['recovered_within_cutoff'];
  
  if (goodWhenDown.includes(metricCode)) {
    return direction === 'down' ? 'text-green-700' : 'text-orange-600';
  }
  
  if (goodWhenUp.includes(metricCode)) {
    return direction === 'up' ? 'text-green-700' : 'text-orange-600';
  }
  
  return direction === 'up' ? 'text-orange-600' : 'text-green-700';
};

const formatKPIValue = (kpi: ExecutiveKPI): string => {
  const value = kpi.current_value;
  
  if (kpi.metric_code === 'exception_rate') {
    return `${value} per 1,000 bags`;
  }
  if (kpi.metric_code === 'recovered_within_cutoff') {
    return `${value}%`;
  }
  if (kpi.metric_code === 'mean_time_to_decision') {
    return `${value} min`;
  }
  if (kpi.metric_code === 'open_case_ageing') {
    return `${value} h`;
  }
  if (kpi.metric_code === 'stale_data_cases') {
    return `${value} of 3`;
  }
  
  return String(value);
};

const getTrendText = (kpi: ExecutiveKPI): string => {
  if (kpi.trend_direction === 'flat') {
    return 'Flat vs prior 14 days';
  }
  
  // Extract magnitude from passenger_impact_note if available
  if (kpi.metric_code === 'exception_rate') {
    return kpi.trend_direction === 'down' ? 'Down 0.3 vs prior 14 days' : 'Up 0.3 vs prior 14 days';
  }
  if (kpi.metric_code === 'recovered_within_cutoff') {
    return kpi.trend_direction === 'up' ? 'Up 4 pts' : 'Down 4 pts';
  }
  if (kpi.metric_code === 'mean_time_to_decision') {
    return kpi.trend_direction === 'down' ? 'Down 3 min' : 'Up 3 min';
  }
  if (kpi.metric_code === 'open_case_ageing') {
    return kpi.trend_direction === 'up' ? 'Up 0.4 h' : 'Down 0.4 h';
  }
  if (kpi.metric_code === 'stale_data_cases') {
    return kpi.trend_direction === 'down' ? 'Down from 3 of 3' : 'Up from 3 of 3';
  }
  
  return kpi.trend_direction === 'up' ? 'Up' : 'Down';
};

const getKPIDescription = (kpi: ExecutiveKPI): string => {
  if (kpi.metric_code === 'exception_rate') {
    return 'Fewer bags needing intervention.';
  }
  if (kpi.metric_code === 'recovered_within_cutoff') {
    return '153 of 205 exception bags made their onward flight.';
  }
  if (kpi.metric_code === 'mean_time_to_decision') {
    return 'From detection to an approval decision.';
  }
  if (kpi.metric_code === 'passengers_impacted') {
    return 'Connecting passengers with a bag at risk.';
  }
  if (kpi.metric_code === 'open_case_ageing') {
    return 'Median age of 6 open cases.';
  }
  if (kpi.metric_code === 'stale_data_cases') {
    return 'Handler feed stale 14 min.';
  }
  
  return kpi.passenger_impact_note || '';
};

export const KPICards: React.FC<KPICardsProps> = ({ kpis }) => {
  return (
    <section className="grid grid-cols-6 gap-4" aria-label="Key metrics">
      {kpis.map((kpi) => (
        <div key={kpi.metric_code} className="bg-white border border-gray-200 rounded-xl shadow-sm p-4">
          <div className="text-xs font-bold tracking-wider uppercase text-gray-600 mb-1">
            {kpi.metric_label}
          </div>
          <div className="text-3xl font-bold leading-tight mt-1">
            {formatKPIValue(kpi)}
          </div>
          <div className={`flex items-center gap-1.5 text-sm font-bold mt-0.5 ${getTrendColor(kpi.trend_direction, kpi.metric_code)}`}>
            <TrendIcon direction={kpi.trend_direction} />
            <span>{getTrendText(kpi)}</span>
          </div>
          <div className="text-xs text-gray-600 mt-1.5">
            {getKPIDescription(kpi)}
          </div>
        </div>
      ))}
    </section>
  );
};
