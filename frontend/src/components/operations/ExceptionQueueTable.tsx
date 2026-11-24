import { CaseRow } from '../../types/operations';

interface ExceptionQueueTableProps {
  cases: CaseRow[];
  selectedCaseRef: string | null;
  onSelectCase: (caseRef: string) => void;
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

export default function ExceptionQueueTable({
  cases,
  selectedCaseRef,
  onSelectCase,
}: ExceptionQueueTableProps) {
  return (
    <div className="bg-white border border-[#D9D5D1] rounded-xl shadow-sm" aria-labelledby="q-h">
      <div className="flex items-center justify-between p-5 border-b border-[#D9D5D1]">
        <h2 id="q-h" className="text-base font-semibold">Prioritised exception queue</h2>
        <span className="text-[#68645F] text-sm">Sorted by passenger impact and time to cutoff</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr>
              <th className="text-left px-3 py-2.5 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">
                Severity
              </th>
              <th className="text-left px-3 py-2.5 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">
                Case
              </th>
              <th className="text-left px-3 py-2.5 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">
                Flight / destination
              </th>
              <th className="text-left px-3 py-2.5 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">
                Time to cutoff
              </th>
              <th className="text-left px-3 py-2.5 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">
                Bags
              </th>
              <th className="text-left px-3 py-2.5 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">
                Pax impact
              </th>
              <th className="text-left px-3 py-2.5 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">
                Primary reason
              </th>
              <th className="text-left px-3 py-2.5 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">
                Freshness
              </th>
              <th className="text-left px-3 py-2.5 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">
                Owner
              </th>
            </tr>
          </thead>
          <tbody>
            {cases.map((caseRow) => (
              <tr
                key={caseRow.case_ref}
                onClick={() => onSelectCase(caseRow.case_ref)}
                className={`cursor-pointer hover:bg-gray-50 ${
                  selectedCaseRef === caseRow.case_ref
                    ? 'bg-[#FBF3F4]'
                    : ''
                }`}
                aria-selected={selectedCaseRef === caseRow.case_ref}
              >
                <td className={`px-3 py-3 border-b border-[#D9D5D1] ${selectedCaseRef === caseRow.case_ref ? 'border-l-4 border-l-[#E7002A]' : ''}`}>
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${getSeverityColor(caseRow.severity)}`}>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 3 2 20h20L12 3z"/>
                      <path d="M12 10v5M12 18v.5"/>
                    </svg>
                    {caseRow.severity.charAt(0).toUpperCase() + caseRow.severity.slice(1)}
                  </span>
                </td>
                <td className="px-3 py-3 border-b border-[#D9D5D1] font-bold">{caseRow.case_ref}</td>
                <td className="px-3 py-3 border-b border-[#D9D5D1]">
                  <div>{caseRow.flight_dest.split('→')[0]?.trim() || caseRow.flight_dest}</div>
                  <div className="text-[#68645F]">{caseRow.flight_dest.includes('→') ? 'Onward ' + caseRow.flight_dest.split('→')[1]?.trim() : ''}</div>
                </td>
                <td className="px-3 py-3 border-b border-[#D9D5D1]">
                  <div className={`font-bold ${caseRow.severity === 'critical' ? 'text-[#B42318]' : ''}`}>
                    {caseRow.time_to_cutoff}
                  </div>
                </td>
                <td className="px-3 py-3 border-b border-[#D9D5D1]">{caseRow.bags}</td>
                <td className="px-3 py-3 border-b border-[#D9D5D1]">{caseRow.pax_impact}</td>
                <td className="px-3 py-3 border-b border-[#D9D5D1]">{caseRow.reason}</td>
                <td className="px-3 py-3 border-b border-[#D9D5D1]">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${
                    caseRow.freshness.includes('Stale') ? 'bg-[#FFF1DE] text-[#A65A00]' : 'bg-[#E3F4EC] text-[#18794E]'
                  }`}>
                    {caseRow.freshness}
                  </span>
                </td>
                <td className="px-3 py-3 border-b border-[#D9D5D1]">{caseRow.owner}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
