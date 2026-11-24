interface CaseHeaderProps {
  caseRef: string;
  exceptionType: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: string;
  bagCount: number;
  station: string;
  timeToDeadline: string;
  deadlineTime: string;
}

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'critical':
      return 'bg-[#FDE9E7] text-[#B42318] border-[#E9B4AE]';
    case 'high':
      return 'bg-[#FFF1DE] text-[#A65A00] border-[#E8C48F]';
    case 'medium':
      return 'bg-[#E6F1FA] text-[#1769AA] border-[#A9CBE6]';
    default:
      return 'bg-[#EEECE9] text-[#231F20] border-[#D9D5D1]';
  }
};

export default function CaseHeader({
  caseRef,
  exceptionType,
  severity,
  status,
  bagCount,
  station,
  timeToDeadline,
  deadlineTime,
}: CaseHeaderProps) {
  return (
    <section className="bg-white border border-[#D9D5D1] rounded-xl shadow-sm p-6 flex items-center gap-5" aria-labelledby="case-h">
      <div className="flex-1">
        <h1 id="case-h" className="text-2xl font-bold mb-2">
          {caseRef} · {exceptionType}
        </h1>
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${getSeverityColor(severity)}`}>
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 3 2 20h20L12 3z"/>
              <path d="M12 10v5M12 18v.5"/>
            </svg>
            {severity.charAt(0).toUpperCase() + severity.slice(1)}
          </span>
          <span className="inline-flex items-center px-2 py-0.5 bg-[#E6F1FA] text-[#1769AA] text-xs font-semibold rounded-full border border-[#A9CBE6]">
            Status: {status}
          </span>
          <span className="inline-flex items-center px-2 py-0.5 bg-[#EEECE9] text-[#231F20] text-xs font-semibold rounded-full border border-[#D9D5D1]">
            {bagCount} bags
          </span>
          <span className="inline-flex items-center px-2 py-0.5 bg-[#EEECE9] text-[#231F20] text-xs font-semibold rounded-full border border-[#D9D5D1]">
            Station {station}
          </span>
        </div>
      </div>

      <div className="text-right">
        <div className="text-xs font-bold tracking-wider text-[#68645F] mb-1">TIME TO BAGGAGE CUTOFF</div>
        <div className="text-3xl font-bold text-[#B42318] flex items-center gap-2 justify-end">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="9"/>
            <path d="M12 7v5l3 2"/>
          </svg>
          {timeToDeadline}
        </div>
        <div className="text-[#68645F] text-sm">{deadlineTime}</div>
      </div>
    </section>
  );
}
