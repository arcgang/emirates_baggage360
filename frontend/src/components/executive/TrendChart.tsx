/**
 * Trend Chart component for executive overview
 * Displays exceptions and recoveries per day as line chart
 */
import { ExecutiveTrendData } from '../../types/executive';

interface TrendChartProps {
  trendData: ExecutiveTrendData;
}

export const TrendChart: React.FC<TrendChartProps> = ({ trendData }) => {
  const { dates, open_case_count, recovered_within_cutoff_pct } = trendData;
  
  if (!dates || dates.length === 0) {
    return (
      <div className="text-sm text-gray-600">
        No trend data available for the selected range.
      </div>
    );
  }
  
  // Calculate scale for chart (exceptions line)
  const maxExceptions = Math.max(...open_case_count, 20);
  const yScale = 220 / maxExceptions; // 220px height for chart area
  
  // Calculate recovered count approximations (for visualization)
  const totalExceptions = open_case_count.reduce((a, b) => a + b, 0);
  const avgRecoveryPct = recovered_within_cutoff_pct.reduce((a, b) => a + b, 0) / recovered_within_cutoff_pct.length;
  const recoveredCounts = open_case_count.map(count => Math.round(count * (avgRecoveryPct / 100)));
  
  // Generate polyline points for exceptions
  const exceptionsPoints = open_case_count
    .map((count, i) => {
      const x = 50 + (i * (730 / (dates.length - 1)));
      const y = 220 - (count * yScale);
      return `${x},${y}`;
    })
    .join(' ');
  
  // Generate polyline points for recoveries
  const recoveriesPoints = recoveredCounts
    .map((count, i) => {
      const x = 50 + (i * (730 / (dates.length - 1)));
      const y = 220 - (count * yScale);
      return `${x},${y}`;
    })
    .join(' ');
  
  // Format date for display
  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
  };
  
  // Sample dates for x-axis (every other day)
  const sampleDates = dates.filter((_, i) => i % 2 === 0);
  
  return (
    <div>
      <div className="flex gap-5 mb-2 text-sm">
        <span className="flex items-center gap-1.5">
          <span className="w-5 h-0 border-t-2 border-black"></span>
          <span>Exceptions (205 bags)</span>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-5 h-0 border-t-2 border-green-700 border-dashed"></span>
          <span>Recovered within cutoff (153 bags)</span>
        </span>
      </div>
      
      <svg viewBox="0 0 800 280" width="100%" role="img" aria-labelledby="chart-title chart-desc" className="block bg-white">
        <title id="chart-title">Exceptions and recoveries per day, {formatDate(dates[0])} to {formatDate(dates[dates.length - 1])}</title>
        <desc id="chart-desc">
          Line chart. Daily exception bags range from {Math.min(...open_case_count)} to {Math.max(...open_case_count)}. 
          Recovered bags range from {Math.min(...recoveredCounts)} to {Math.max(...recoveredCounts)}. 
          Recoveries stay below exceptions every day.
        </desc>
        
        {/* Grid lines */}
        <g stroke="#D9D5D1" strokeWidth="1">
          <line x1="50" y1="20" x2="780" y2="20"/>
          <line x1="50" y1="70" x2="780" y2="70"/>
          <line x1="50" y1="120" x2="780" y2="120"/>
          <line x1="50" y1="170" x2="780" y2="170"/>
          <line x1="50" y1="220" x2="780" y2="220"/>
        </g>
        
        {/* Y-axis labels */}
        <g fontSize="12" fill="#68645F" textAnchor="end">
          <text x="42" y="224">0</text>
          <text x="42" y="174">5</text>
          <text x="42" y="124">10</text>
          <text x="42" y="74">15</text>
          <text x="42" y="24">20</text>
        </g>
        
        {/* Exceptions line (solid black) */}
        <polyline 
          fill="none" 
          stroke="#231F20" 
          strokeWidth="3" 
          points={exceptionsPoints}
        />
        
        {/* Recoveries line (dashed green) */}
        <polyline 
          fill="none" 
          stroke="#18794E" 
          strokeWidth="3" 
          strokeDasharray="8 5"
          points={recoveriesPoints}
        />
        
        {/* Highlight points and labels for key dates */}
        {open_case_count.map((count, i) => {
          if (i % 3 === 0 || i === open_case_count.length - 1) {
            const x = 50 + (i * (730 / (dates.length - 1)));
            const y = 220 - (count * yScale);
            return (
              <g key={i}>
                <circle cx={x} cy={y} r="4" fill="#231F20"/>
                <text x={x} y={y - 8} fontSize="12" fill="#231F20" fontWeight="700" textAnchor="middle">
                  {count}
                </text>
              </g>
            );
          }
          return null;
        })}
        
        {/* X-axis date labels */}
        <g fontSize="12" fill="#68645F" textAnchor="middle">
          {sampleDates.map((dateStr, i) => {
            const originalIndex = dates.indexOf(dateStr);
            const x = 50 + (originalIndex * (730 / (dates.length - 1)));
            return (
              <text key={i} x={x} y="242">
                {formatDate(dateStr)}
              </text>
            );
          })}
          <text x={50 + (730 / (dates.length - 1)) * (dates.length - 1)} y="258">
            {formatDate(dates[dates.length - 1])}
          </text>
        </g>
        
        {/* Chart label */}
        <text x="415" y="274" fontSize="12" fill="#68645F" textAnchor="middle">
          Bags per day · SIMULATED
        </text>
      </svg>
    </div>
  );
};
