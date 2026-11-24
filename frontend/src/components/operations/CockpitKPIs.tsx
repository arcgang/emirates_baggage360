import { KPIMetric } from '../../types/operations';

interface CockpitKPIsProps {
  metrics: KPIMetric[];
}

export default function CockpitKPIs({ metrics }: CockpitKPIsProps) {
  return (
    <div className="grid grid-cols-4 gap-4" role="region" aria-label="Cockpit summary">
      {metrics.map((metric, index) => (
        <div
          key={index}
          className={`bg-white border border-[#D9D5D1] rounded-xl shadow-sm p-4 ${
            metric.urgent ? 'border-l-4 border-l-[#B42318]' : ''
          }`}
        >
          <div className="text-xs font-bold tracking-wider uppercase text-[#68645F] mb-1">
            {metric.urgent && (
              <svg className="inline w-4 h-4 mr-1 stroke-current" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none">
                <path d="M12 3 2 20h20L12 3z"/>
                <path d="M12 10v5M12 18v.5"/>
              </svg>
            )}
            {metric.label}
          </div>
          <div className="text-4xl font-bold leading-none my-1">{metric.value}</div>
          <div className="text-xs text-[#68645F]">{metric.note}</div>
        </div>
      ))}
    </div>
  );
}
