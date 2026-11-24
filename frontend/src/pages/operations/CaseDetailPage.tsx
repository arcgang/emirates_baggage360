import { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../../lib/api-client';
import CaseHeader from '../../components/operations/CaseHeader';
import BagTimeline from '../../components/operations/BagTimeline';
import RecommendationCard from '../../components/operations/RecommendationCard';
import ApprovalForm from '../../components/operations/ApprovalForm';
import { BagTimeline as BagTimelineType, Recommendation, ApprovalDecisionRequest, AuditEvent } from '../../types/operations';

export default function CaseDetailPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const [activeBagId, setActiveBagId] = useState('00000000-0000-0000-0000-000000000193');
  const [activeTab, setActiveTab] = useState<'overview' | 'tasks' | 'audit'>('audit');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [createdTasks, setCreatedTasks] = useState<string[]>([]);

  // Mock data matching seed
  const mockTimelines: BagTimelineType[] = [
    {
      bag_id: '00000000-0000-0000-0000-000000000193',
      bag_tag: '0176 482193',
      passenger_name_masked: 'PAX-***-001',
      journey_context: {
        journey_id: '00000000-0000-0000-0000-000000000065',
        inbound_flight: 'EK 0201 from JFK',
        onward_flight: 'EK 0507 to JNB',
        connection_window_minutes: 42,
        gate_change: 'B14 → B22',
        stand_change: null,
        aircraft_change: null,
      },
      milestones: [
        {
          event_type: 'Accepted at origin check-in',
          observed_at: new Date(Date.now() - 14 * 60 * 60 * 1000).toISOString(),
          source_system: 'Wasla',
          fact_type: 'observed',
          freshness_state: 'fresh',
          location_code: 'JFK',
        },
        {
          event_type: 'Loaded on EK 0201',
          observed_at: new Date(Date.now() - 13 * 60 * 60 * 1000).toISOString(),
          source_system: 'BHS',
          fact_type: 'observed',
          freshness_state: 'fresh',
          location_code: 'JFK',
        },
        {
          event_type: 'Arrived DXB',
          observed_at: new Date(Date.now() - 75 * 60 * 1000).toISOString(),
          source_system: 'Flight operations',
          fact_type: 'observed',
          freshness_state: 'fresh',
          location_code: 'DXB',
        },
        {
          event_type: 'Transfer scan DXB',
          observed_at: new Date(Date.now() - 14 * 60 * 1000).toISOString(),
          source_system: 'Flight operations',
          fact_type: 'derived',
          freshness_state: 'awaiting_confirmation',
          location_code: 'DXB',
        },
        {
          event_type: 'Load on EK 0507',
          observed_at: new Date(Date.now() + 36 * 60 * 1000).toISOString(),
          source_system: 'Predicted',
          fact_type: 'estimated',
          freshness_state: 'fresh',
          location_code: 'DXB',
        },
      ],
    },
    {
      bag_id: '00000000-0000-0000-0000-000000000194',
      bag_tag: '0176 482194',
      passenger_name_masked: 'PAX-***-001',
      journey_context: null,
      milestones: [
        {
          event_type: 'Accepted at origin',
          observed_at: new Date(Date.now() - 14 * 60 * 60 * 1000).toISOString(),
          source_system: 'Wasla',
          fact_type: 'observed',
          freshness_state: 'fresh',
          location_code: 'JFK',
        },
      ],
    },
    {
      bag_id: '00000000-0000-0000-0000-000000000195',
      bag_tag: '0176 482195',
      passenger_name_masked: 'PAX-***-002',
      journey_context: null,
      milestones: [
        {
          event_type: 'Accepted at origin',
          observed_at: new Date(Date.now() - 14 * 60 * 60 * 1000).toISOString(),
          source_system: 'Wasla',
          fact_type: 'observed',
          freshness_state: 'fresh',
          location_code: 'JFK',
        },
      ],
    },
  ];

  const mockRecommendations: Recommendation[] = [
    {
      recommendation_id: '00000000-0000-0000-0000-000000000259',
      case_id: caseId || '',
      action_code: 'PRIORITY_TRANSFER',
      action_label: 'R1 · Priority transfer to EK 0507',
      reason_text: '42 min connection against 60 min minimum, and no transfer scan yet. Move all 3 bags to the priority belt for EK 0507.',
      confidence_score: 0.78,
      freshness_state: 'fresh',
      evidence: [
        'EK 0201 arrived 19:58 (OBSERVED, flight ops)',
        'Gate change B14 → B22 adds walking and transfer time (OBSERVED)',
        'No DXB transfer scan after 14 min (INFERRED)',
      ],
      generated_at: new Date(Date.now() - 4 * 60 * 1000).toISOString(),
      superseded_at: null,
    },
    {
      recommendation_id: '00000000-0000-0000-0000-00000000025a',
      case_id: caseId || '',
      action_code: 'MONITOR',
      action_label: 'R2 · Fallback: rebook-ready reflight hold',
      reason_text: 'If R1 misses the cutoff, hold bags for the next available departure.',
      confidence_score: 0.64,
      freshness_state: 'fresh',
      evidence: [
        'Connection window 42 min',
        'Next JNB departure available',
      ],
      generated_at: new Date(Date.now() - 4 * 60 * 1000).toISOString(),
      superseded_at: null,
    },
  ];

  const mockAuditEvents: AuditEvent[] = [
    {
      audit_event_id: '1',
      actor_user_id: 'system',
      action_type: 'recommendation_generated',
      entity_type: 'exception_case',
      entity_id: caseId || '',
      correlation_id: 'corr-91d2a7',
      outcome_code: 'success',
      detail: { recommendations: ['R1', 'R2'] },
      occurred_at: new Date(Date.now() - 61 * 60 * 1000).toISOString(),
    },
  ];

  const handleApprovalSubmit = async (request: ApprovalDecisionRequest) => {
    setIsSubmitting(true);
    try {
      const response = await apiClient.post<any>(`/operations/cases/${caseId}/approvals`, request);
      // Extract task IDs from response
      if (response.tasks_created && response.tasks_created.length > 0) {
        const taskIds = response.tasks_created.map((t: any) => {
          // Format task ID as TSK-{STATION}-{number}
          const taskId = t.task_id;
          const station = t.station_code || 'DXB';
          const uuid_last_segment = taskId.split('-')[4];
          const task_number = parseInt(uuid_last_segment, 16);
          return `TSK-${station}-${task_number}`;
        });
        setCreatedTasks(taskIds);
      }
      // Show success state
      alert(`Approval recorded successfully. Created ${response.tasks_created?.length || 0} task(s).`);
    } catch (error) {
      console.error('Approval failed:', error);
      alert('Approval submission failed');
    } finally {
      setIsSubmitting(false);
    }
  };

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
                className="flex items-center gap-2.5 h-11 px-3 rounded-lg text-[#E4E0DC] font-semibold hover:bg-[#3A3536]"
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
          <nav className="text-sm" aria-label="Breadcrumb">
            <Link to="/operations/cockpit" className="font-semibold text-[#1769AA] hover:underline">Cockpit</Link>
            {' › '}
            <strong>BC-DXB-240611</strong>
          </nav>
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
          <CaseHeader
            caseRef="BC-DXB-240611"
            exceptionType="Connection at risk, late inbound"
            severity="critical"
            status="under_review"
            bagCount={3}
            station="DXB"
            timeToDeadline="36 min"
            deadlineTime="Cutoff 20:40 GST · 16:40Z"
          />

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white border border-[#D9D5D1] rounded-xl shadow-sm p-5">
              <h2 className="text-xs font-bold tracking-wider uppercase text-[#68645F] mb-2">
                Observed state <span className="inline-block px-1.5 py-0.5 bg-[#E3F4EC] text-[#18794E] text-[10.5px] font-bold tracking-wide border border-[#9FD2B8] rounded ml-1">OBSERVED</span>
              </h2>
              <p className="text-sm">Hero bag arrived at DXB on EK 0201 at 19:58. The DXB transfer scan has not been seen yet.</p>
            </div>
            <div className="bg-white border border-[#D9D5D1] rounded-xl shadow-sm p-5">
              <h2 className="text-xs font-bold tracking-wider uppercase text-[#68645F] mb-2">
                Predicted state <span className="inline-block px-1.5 py-0.5 bg-white text-[#A65A00] text-[10.5px] font-bold tracking-wide border border-dashed border-[#A65A00] rounded ml-1">PREDICTED</span>
              </h2>
              <p className="text-sm">Without action, the bag is unlikely to make the EK 0507 baggage cutoff. This is a prediction, not a confirmed outcome.</p>
            </div>
          </div>

          <div className="grid grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)] gap-5 items-start">
            <div className="flex flex-col gap-5">
              {/* Journey Context */}
              <div className="bg-white border border-[#D9D5D1] rounded-xl shadow-sm p-5" aria-labelledby="ctx-h">
                <h2 id="ctx-h" className="text-base font-semibold mb-3">Journey context</h2>
                <div className="grid grid-cols-[1fr_auto_1fr] gap-3 items-center mb-4">
                  <div className="p-3 border border-[#D9D5D1] rounded-lg bg-[#F7F6F4]">
                    <div className="text-xs font-bold tracking-wider uppercase text-[#68645F]">Inbound</div>
                    <div className="text-xl font-bold">EK 0201</div>
                    <div className="text-sm">Arrived 19:58 GST · 32 min late</div>
                  </div>
                  <div className="text-center text-xs">
                    <strong className="block text-xl text-[#B42318]">42 min</strong>
                    connection vs 60 min minimum<br/>Gate B14 → B22
                  </div>
                  <div className="p-3 border border-[#D9D5D1] rounded-lg bg-[#F7F6F4]">
                    <div className="text-xs font-bold tracking-wider uppercase text-[#68645F]">Onward</div>
                    <div className="text-xl font-bold">EK 0507</div>
                    <div className="text-sm">Departs 21:10 GST · cutoff 20:40</div>
                  </div>
                </div>
                <div className="flex gap-2 flex-wrap" aria-label="Source freshness">
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-[#E3F4EC] text-[#18794E] text-xs font-semibold rounded-full">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="9"/>
                      <path d="m8 12 3 3 5-6"/>
                    </svg>
                    Wasla · fresh 6 min
                  </span>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-[#E3F4EC] text-[#18794E] text-xs font-semibold rounded-full">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="9"/>
                      <path d="m8 12 3 3 5-6"/>
                    </svg>
                    BHS/BRS · fresh 4 min
                  </span>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-[#FFF1DE] text-[#A65A00] text-xs font-semibold rounded-full">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 3 2 20h20L12 3z"/>
                      <path d="M12 10v5M12 18v.5"/>
                    </svg>
                    Handler feed · stale 14 min
                  </span>
                </div>
              </div>

              <BagTimeline
                timelines={mockTimelines}
                activeBagId={activeBagId}
                onSelectBag={setActiveBagId}
              />
            </div>

            <div className="flex flex-col gap-5">
              {/* Recommendations */}
              <div className="bg-white border border-[#D9D5D1] rounded-xl shadow-sm p-5" aria-labelledby="rec-h">
                <h2 id="rec-h" className="text-base font-semibold mb-3">Recommendations</h2>
                <div className="flex flex-col gap-3">
                  {mockRecommendations.map((rec, index) => (
                    <RecommendationCard key={rec.recommendation_id} recommendation={rec} isTop={index === 0} />
                  ))}
                </div>
              </div>

              <ApprovalForm
                recommendationId={mockRecommendations[0].recommendation_id}
                recommendationLabel={mockRecommendations[0].action_label}
                onSubmit={handleApprovalSubmit}
                isSubmitting={isSubmitting}
              />
              
              {createdTasks.length > 0 && (
                <div className="mt-4 p-4 bg-[#E3F4EC] border border-[#9FD2B8] rounded-lg">
                  <div className="flex gap-2 items-start">
                    <svg className="w-5 h-5 text-[#18794E] flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="9"/>
                      <path d="m8 12 3 3 5-6"/>
                    </svg>
                    <div>
                      <div className="font-semibold text-[#18794E]">Approval successful</div>
                      <div className="text-sm text-[#18794E] mt-1">
                        Created {createdTasks.length} task(s): {createdTasks.join(', ')}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Tasks and Audit Trail */}
          <div className="bg-white border border-[#D9D5D1] rounded-xl shadow-sm p-5" aria-labelledby="tabs-h">
            <h2 id="tabs-h" className="text-base font-semibold mb-2">Tasks and audit trail</h2>
            <div className="flex gap-1 border-b border-[#D9D5D1] mb-4" role="tablist" aria-label="Case sections">
              <button
                role="tab"
                aria-current={activeTab === 'overview' ? 'true' : 'false'}
                onClick={() => setActiveTab('overview')}
                className={`inline-flex items-center h-9 px-3 font-semibold text-sm border-b-3 ${
                  activeTab === 'overview'
                    ? 'text-[#231F20] border-b-[#E7002A]'
                    : 'text-[#68645F] border-b-transparent'
                }`}
              >
                Overview
              </button>
              <button
                role="tab"
                aria-current={activeTab === 'tasks' ? 'true' : 'false'}
                onClick={() => setActiveTab('tasks')}
                className={`inline-flex items-center h-9 px-3 font-semibold text-sm border-b-3 ${
                  activeTab === 'tasks'
                    ? 'text-[#231F20] border-b-[#E7002A]'
                    : 'text-[#68645F] border-b-transparent'
                }`}
              >
                Tasks (pre-decision: 0 · after approval: 1)
              </button>
              <button
                role="tab"
                aria-current={activeTab === 'audit' ? 'true' : 'false'}
                onClick={() => setActiveTab('audit')}
                className={`inline-flex items-center h-9 px-3 font-semibold text-sm border-b-3 ${
                  activeTab === 'audit'
                    ? 'text-[#231F20] border-b-[#E7002A]'
                    : 'text-[#68645F] border-b-transparent'
                }`}
              >
                Audit trail
              </button>
            </div>

            {activeTab === 'audit' && (
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="text-left px-3 py-2 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">Time (GST / UTC)</th>
                    <th className="text-left px-3 py-2 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">Action</th>
                    <th className="text-left px-3 py-2 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">Actor</th>
                    <th className="text-left px-3 py-2 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">Entity</th>
                    <th className="text-left px-3 py-2 bg-[#EEECE9] text-[11.5px] tracking-wider uppercase text-[#68645F] font-bold border-b border-[#D9D5D1]">Correlation ID</th>
                  </tr>
                </thead>
                <tbody>
                  {mockAuditEvents.map((event) => (
                    <tr key={event.audit_event_id}>
                      <td className="px-3 py-3 border-b border-[#D9D5D1]">{new Date(event.occurred_at).toLocaleString()}</td>
                      <td className="px-3 py-3 border-b border-[#D9D5D1]">{event.action_type}</td>
                      <td className="px-3 py-3 border-b border-[#D9D5D1]">{event.actor_user_id}</td>
                      <td className="px-3 py-3 border-b border-[#D9D5D1]">{event.entity_type} {event.entity_id.substring(0, 8)}...</td>
                      <td className="px-3 py-3 border-b border-[#D9D5D1]">{event.correlation_id}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
