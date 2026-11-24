import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import CockpitKPIs from '../../components/operations/CockpitKPIs';
import ExceptionQueueTable from '../../components/operations/ExceptionQueueTable';
import { KPIMetric, CaseRow } from '../../types/operations';

export default function CockpitPage() {
  const navigate = useNavigate();
  const [selectedCaseRef, setSelectedCaseRef] = useState<string | null>('BC-DXB-240611');
  const [staleDataBanner, setStaleDataBanner] = useState(true);

  // Mock KPI data matching wireframe
  const kpis: KPIMetric[] = [
    { label: 'Open cases', value: 6, note: 'In this bank window' },
    { label: 'Urgent', value: 2, note: 'Cutoff within 60 min', urgent: true },
    { label: 'Impacted bags', value: 11, note: 'Grouped by shared cause' },
    { label: 'Impacted passengers', value: 9, note: 'Connecting passengers at risk' },
  ];

  // Mock case queue data matching seed data
  const cases: CaseRow[] = [
    {
      severity: 'critical',
      case_ref: 'BC-DXB-240611',
      flight_dest: 'EK 0201 → EK 0507 to JNB',
      time_to_cutoff: '36 min',
      bags: 3,
      pax_impact: 'High · 3 pax',
      reason: 'Connection at risk, late inbound',
      freshness: 'Stale 14 min',
      owner: 'M. Al Suwaidi',
    },
    {
      severity: 'high',
      case_ref: 'BC-DXB-240612',
      flight_dest: 'EK 0412 → EK 0619 to BOM',
      time_to_cutoff: '52 min',
      bags: 2,
      pax_impact: 'High · 2 pax',
      reason: 'Transfer scan missing',
      freshness: 'Stale 14 min',
      owner: 'Unassigned',
    },
    {
      severity: 'high',
      case_ref: 'BC-DXB-240613',
      flight_dest: 'EK 0087 → EK 0331 to LHR',
      time_to_cutoff: '1 h 25 min',
      bags: 2,
      pax_impact: 'Medium · 2 pax',
      reason: 'Misroute suspected, belt 7',
      freshness: 'Fresh 3 min',
      owner: 'Unassigned',
    },
    {
      severity: 'medium',
      case_ref: 'BC-DXB-240614',
      flight_dest: 'EK 0553 → EK 0742 to SIN',
      time_to_cutoff: '2 h 10 min',
      bags: 1,
      pax_impact: 'Low · 1 pax',
      reason: 'Customs hold',
      freshness: 'Fresh 5 min',
      owner: 'Unassigned',
    },
  ];

  const selectedCase = cases.find((c) => c.case_ref === selectedCaseRef);

  return (
    <div className="min-h-screen flex" style={{ background: '#F7F6F4' }}>
      {/* Sidebar */}
      <aside className="w-60 flex-shrink-0 bg-[#231F20] text-[#E4E0DC] p-6 flex flex-col gap-6">
        <div className="flex items-center gap-2.5 text-white font-bold text-lg">
          <div className="w-8 h-8 bg-[#E7002A] rounded-lg flex items-center justify-center">
            <svg className="w-4 h-4 stroke-white fill-none" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="4" y="7" width="16" height="13" rx="2"/>
              <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M4 13h16"/>
            </svg>
          </div>
          Baggage360
        </div>

        <nav aria-label="Operations navigation">
          <ul className="flex flex-col gap-1">
            <li>
              <Link
                to="/operations/cockpit"
                aria-current="page"
                className="flex items-center gap-2.5 h-11 px-3 rounded-lg bg-[#3A3536] text-white font-semibold border-l-4 border-l-[#E7002A]"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="7" height="7"/>
                  <rect x="14" y="3" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/>
                  <rect x="14" y="14" width="7" height="7"/>
                </svg>
                Cockpit
              </Link>
            </li>
            <li>
              <Link
                to="/dashboard"
                className="flex items-center gap-2.5 h-11 px-3 rounded-lg text-[#E4E0DC] font-semibold hover:bg-[#3A3536]"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M8 6h12M8 12h12M8 18h12M4 6h.5M4 12h.5M4 18h.5"/>
                </svg>
                Dashboard
              </Link>
            </li>
          </ul>
        </nav>

        <div className="mt-auto p-3 border border-[#4A4546] rounded-lg text-xs">
          <span className="inline-flex items-center px-2 py-0.5 bg-[#EEECE9] text-[#231F20] text-xs font-semibold rounded-full border border-[#D9D5D1] mb-2">Role: Operations Lead</span>
          <div className="text-sm font-bold text-white">M. Al Suwaidi</div>
          <div>DXB Baggage Operations Lead</div>
          <div>Purpose: Operational recovery</div>
          <Link to="/login" className="text-white underline">Sign out</Link>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="flex items-center gap-4 px-6 py-3 bg-white border-b border-[#D9D5D1]">
          <h1 className="text-xl font-semibold">Operations cockpit</h1>
          <span className="inline-flex items-center gap-2 h-9 px-3 border border-[#8A857F] rounded-lg bg-white font-semibold text-sm">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 21s7-6 7-11a7 7 0 0 0-14 0c0 5 7 11 7 11z"/>
              <circle cx="12" cy="10" r="2.5"/>
            </svg>
            Station: DXB ▾
          </span>
          <span className="inline-flex items-center gap-2 h-9 px-3 border border-[#8A857F] rounded-lg bg-white font-semibold text-sm">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9"/>
              <path d="M12 7v5l3 2"/>
            </svg>
            Bank window: Current + next 2h ▾
          </span>
          <div className="ml-auto flex items-center gap-3">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-[#FFF1DE] text-[#A65A00] text-xs font-semibold rounded-full border border-[#E8C48F]">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3 2 20h20L12 3z"/>
                <path d="M12 10v5M12 18v.5"/>
              </svg>
              Sources fresh 2 of 3 · Mixed
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 border border-dashed border-[#A65A00] rounded bg-[#FFF1DE] text-[#A65A00] text-xs font-bold tracking-wider">SIMULATED</span>
            <span className="text-[#68645F] font-semibold">20:04 GST (UTC+4)</span>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="p-6 flex flex-col gap-5">
          {staleDataBanner && (
            <div className="flex gap-2 items-start p-3 rounded-lg bg-[#FFF1DE] text-[#A65A00] border border-[#E8C48F]" role="status">
              <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3 2 20h20L12 3z"/>
                <path d="M12 10v5M12 18v.5"/>
              </svg>
              <span className="text-sm">
                <strong>Transfer scan source stale 14 min.</strong> Predictions that depend on DXB transfer scans may be outdated. Observed milestones are unaffected.
              </span>
            </div>
          )}

          <CockpitKPIs metrics={kpis} />

          <div className="grid grid-cols-[minmax(0,1fr)_400px] gap-5 items-start">
            <ExceptionQueueTable
              cases={cases}
              selectedCaseRef={selectedCaseRef}
              onSelectCase={setSelectedCaseRef}
            />

            {/* Case Preview Panel */}
            {selectedCase && (
              <div className="bg-white border border-[#D9D5D1] rounded-xl shadow-sm p-5 flex flex-col gap-4" aria-labelledby="pv-h">
                <div className="flex justify-between items-center">
                  <h2 id="pv-h" className="text-base font-semibold">Selected: {selectedCase.case_ref}</h2>
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${
                    selectedCase.severity === 'critical' ? 'bg-[#FDE9E7] text-[#B42318] border-[#E9B4AE]' : 'bg-[#FFF1DE] text-[#A65A00] border-[#E8C48F]'
                  }`}>
                    {selectedCase.severity.charAt(0).toUpperCase() + selectedCase.severity.slice(1)}
                  </span>
                </div>

                <dl className="grid grid-cols-[120px_1fr] gap-y-1.5 gap-x-3 text-sm">
                  <dt className="text-[#68645F]">Exception</dt>
                  <dd className="font-semibold">{selectedCase.reason}</dd>
                  <dt className="text-[#68645F]">Flight</dt>
                  <dd className="font-semibold">{selectedCase.flight_dest}</dd>
                  <dt className="text-[#68645F]">Time to cutoff</dt>
                  <dd className="font-semibold">{selectedCase.time_to_cutoff}</dd>
                  <dt className="text-[#68645F]">Bags</dt>
                  <dd className="font-semibold">{selectedCase.bags}</dd>
                  <dt className="text-[#68645F]">Pax impact</dt>
                  <dd className="font-semibold">{selectedCase.pax_impact}</dd>
                </dl>

                <div>
                  <h3 className="text-sm font-semibold mb-2">Hero bag timeline preview</h3>
                  <ol className="space-y-2.5 border-l-2 border-[#D9D5D1] ml-1.5 pl-4">
                    <li className="relative text-xs">
                      <div className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-[#18794E] border-2 border-white shadow-sm"></div>
                      <div>Accepted at origin 14:05 <span className="inline-block px-1.5 py-0.5 bg-[#E3F4EC] text-[#18794E] text-[10.5px] font-bold tracking-wide border border-[#9FD2B8] rounded">OBSERVED</span></div>
                    </li>
                    <li className="relative text-xs">
                      <div className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-[#18794E] border-2 border-white shadow-sm"></div>
                      <div>Arrived DXB 19:58 <span className="inline-block px-1.5 py-0.5 bg-[#E3F4EC] text-[#18794E] text-[10.5px] font-bold tracking-wide border border-[#9FD2B8] rounded">OBSERVED</span></div>
                    </li>
                    <li className="relative text-xs text-[#68645F]">
                      <div className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-white border-2 border-[#A65A00]"></div>
                      <div>Transfer scan awaiting (stale 14 min) <span className="inline-block px-1.5 py-0.5 bg-[#E6F1FA] text-[#1769AA] text-[10.5px] font-bold tracking-wide border border-[#A9CBE6] rounded">INFERRED</span></div>
                    </li>
                  </ol>
                </div>

                <div className="p-3 border border-[#D9D5D1] rounded-lg bg-[#F7F6F4]">
                  <div className="flex justify-between items-center mb-1">
                    <strong className="text-sm">Top recommendation</strong>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-[#EEECE9] text-[#231F20] text-xs font-semibold rounded-full border border-[#D9D5D1]">
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="5" y="11" width="14" height="9" rx="2"/>
                        <path d="M8 11V8a4 4 0 0 1 8 0v3"/>
                      </svg>
                      Requires approval
                    </span>
                  </div>
                  <p className="text-xs">Priority transfer to EK 0507 · confidence 0.78 · freshness 4 min</p>
                </div>

                <button
                  onClick={() => navigate(`/operations/cases/${selectedCase.case_ref}`)}
                  className="h-11 bg-[#E7002A] text-white font-semibold rounded-lg flex items-center justify-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M13 6l6 6-6 6"/>
                  </svg>
                  Open case
                </button>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
