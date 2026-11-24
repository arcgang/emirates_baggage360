import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import TaskHeader from '../../components/partner/TaskHeader';
import EvidenceForm from '../../components/partner/EvidenceForm';
import { PartnerTaskDetail, TaskEventRequest, TaskEvidence } from '../../types/partner';
import { apiClient } from '../../lib/api-client';

export default function TaskDetailPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const [task, setTask] = useState<PartnerTaskDetail | null>(null);
  const [evidence, setEvidence] = useState<TaskEvidence[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [acknowledging, setAcknowledging] = useState(false);

  const loadTask = async () => {
    if (!taskId) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await apiClient.get<PartnerTaskDetail>(`/partner/tasks/${taskId}`);
      setTask(response);
    } catch (err) {
      if (err instanceof Error) {
        if (err.message.includes('403')) {
          setError('This task is not assigned to your role.');
        } else if (err.message.includes('404')) {
          setError('We could not find that task.');
        } else {
          setError('Failed to load task details.');
        }
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTask();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]);

  const handleAcknowledge = async () => {
    if (!taskId) return;
    
    setAcknowledging(true);
    
    try {
      const clientEventId = `CLIENT-EVT-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      await apiClient.post(`/partner/tasks/${taskId}/events`, {
        event_type: 'acknowledged',
        client_event_id: clientEventId,
      });
      
      // Reload task to get updated status
      await loadTask();
    } catch (err) {
      setError('Failed to acknowledge task. Please try again.');
    } finally {
      setAcknowledging(false);
    }
  };

  const handleEvidenceSubmit = async (event: TaskEventRequest) => {
    if (!taskId) return;
    
    await apiClient.post(`/partner/tasks/${taskId}/events`, event);
    
    // Reload task to get updated status
    await loadTask();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#F7F6F4' }}>
        <div className="text-center">
          <div className="mb-2 text-base font-semibold">Loading task details…</div>
          <div className="space-y-2">
            <div className="h-3 bg-[#EEECE9] rounded w-64 mx-auto"></div>
            <div className="h-3 bg-[#EEECE9] rounded w-48 mx-auto"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col" style={{ background: '#F7F6F4' }}>
        {/* Top Nav */}
        <header className="flex items-center gap-6 px-8 min-h-16 bg-[#231F20] text-white">
          <div className="flex items-center gap-2.5 font-bold text-lg">
            <div className="w-8 h-8 bg-[#E7002A] rounded-lg flex items-center justify-center">
              <svg className="w-4 h-4 stroke-white fill-none" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="4" y="7" width="16" height="13" rx="2"/>
                <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M4 13h16"/>
              </svg>
            </div>
            Baggage360
          </div>

          <nav aria-label="Partner">
            <Link to="/partner/tasks" className="inline-flex items-center min-h-16 px-2 text-white font-semibold">
              My tasks
            </Link>
          </nav>

          <div className="ml-auto flex items-center gap-4 text-sm">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 border border-dashed border-[#A65A00] rounded bg-[#FFF1DE] text-[#A65A00] text-xs font-bold tracking-wider">SIMULATED</span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#3A3536] text-white border-[#5A5552]">Handler Supervisor, Transfer Area · DXB</span>
            <span>{new Date().toLocaleTimeString('en-GB', { timeZone: 'Asia/Dubai', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}</span>
            <Link to="/login" className="text-white font-semibold">Sign out</Link>
          </div>
        </header>

        <main className="p-6 flex-1">
          <nav className="text-sm mb-5" aria-label="Breadcrumb">
            <Link to="/partner/tasks" className="font-semibold">My tasks</Link> › <strong>{taskId || 'Task'}</strong>
          </nav>

          <div className="flex gap-2 items-start p-3 rounded-lg bg-[#FDE9E7] text-[#B42318] border border-[#E9B4AE]" role="alert">
            <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {error.includes('not assigned') ? (
                <>
                  <rect x="5" y="11" width="14" height="9" rx="2"/>
                  <path d="M8 11V8a4 4 0 0 1 8 0v3"/>
                </>
              ) : (
                <>
                  <path d="M12 3 2 20h20L12 3z"/>
                  <path d="M12 10v5M12 18v.5"/>
                </>
              )}
            </svg>
            <span>{error}</span>
          </div>

          <Link
            to="/partner/tasks"
            className="inline-flex items-center gap-2 min-h-9 px-3 mt-4 rounded-lg font-semibold text-sm border border-[#D9D5D1] bg-white"
          >
            Back to My tasks
          </Link>
        </main>
      </div>
    );
  }

  if (!task) return null;

  // Parse flight context for display
  const flightLines = task.flight_context.split('\n');

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#F7F6F4' }}>
      {/* Top Nav */}
      <header className="flex items-center gap-6 px-8 min-h-16 bg-[#231F20] text-white">
        <div className="flex items-center gap-2.5 font-bold text-lg">
          <div className="w-8 h-8 bg-[#E7002A] rounded-lg flex items-center justify-center">
            <svg className="w-4 h-4 stroke-white fill-none" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="4" y="7" width="16" height="13" rx="2"/>
              <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M4 13h16"/>
            </svg>
          </div>
          Baggage360
        </div>

        <nav aria-label="Partner">
          <Link to="/partner/tasks" className="inline-flex items-center min-h-16 px-2 text-white font-semibold">
            My tasks
          </Link>
        </nav>

        <div className="ml-auto flex items-center gap-4 text-sm">
          <span className="inline-flex items-center gap-1 px-2 py-0.5 border border-dashed border-[#A65A00] rounded bg-[#FFF1DE] text-[#A65A00] text-xs font-bold tracking-wider">SIMULATED</span>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#3A3536] text-white border-[#5A5552]">Handler Supervisor, Transfer Area · DXB</span>
          <span>{new Date().toLocaleTimeString('en-GB', { timeZone: 'Asia/Dubai', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}</span>
          <Link to="/login" className="text-white font-semibold">Sign out</Link>
        </div>
      </header>

      {/* Main Content */}
      <main id="main" className="p-6 flex flex-col gap-5">
        <nav className="text-sm" aria-label="Breadcrumb">
          <Link to="/partner/tasks" className="font-semibold">My tasks</Link> › <strong>{task.task_id}</strong>
        </nav>

        <TaskHeader task={task} />

        <div className="grid grid-cols-2 gap-5 items-start">
          <div className="flex flex-col gap-5">
            <section className="p-5 bg-white border border-[#D9D5D1] rounded-xl shadow-sm" aria-labelledby="slice-h">
              <h2 id="slice-h" className="text-base font-semibold mb-3">Your view of the case</h2>
              <dl className="grid grid-cols-[160px_1fr] gap-y-2 gap-x-3 text-sm">
                <dt className="text-[#68645F]">Bag reference</dt>
                <dd className="font-semibold">{task.bag_reference}</dd>
                {flightLines.map((line, idx) => {
                  if (idx === 0) {
                    return (
                      <>
                        <dt key={`dt-${idx}`} className="text-[#68645F]">{line.includes('→') ? 'Flight' : 'Context'}</dt>
                        <dd key={`dd-${idx}`} className="font-semibold">{line}</dd>
                      </>
                    );
                  }
                  return (
                    <>
                      <dt key={`dt-${idx}`} className="text-[#68645F]"></dt>
                      <dd key={`dd-${idx}`} className="font-semibold text-[#68645F]">{line}</dd>
                    </>
                  );
                })}
                <dt className="text-[#68645F]">Station</dt>
                <dd className="font-semibold">{task.station_code}</dd>
                <dt className="text-[#68645F]">Case reference</dt>
                <dd className="font-semibold">{task.case_reference}</dd>
              </dl>
              <div className="mt-4 p-3 border border-dashed border-[#68645F] rounded-lg text-sm" role="note">
                <strong className="flex items-center gap-1.5 mb-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  Hidden from your role
                </strong>
                <ul className="text-[#68645F] text-xs space-y-0.5">
                  <li>– Passenger name and booking reference</li>
                  <li>– Risk scores and confidence values</li>
                  <li>– Internal notes and other cases</li>
                </ul>
              </div>
            </section>

            <section className="p-5 bg-white border border-[#D9D5D1] rounded-xl shadow-sm" aria-labelledby="ins-h">
              <h2 id="ins-h" className="text-base font-semibold mb-3">Instructions</h2>
              <ol className="space-y-2" style={{ counterReset: 's' }}>
                {task.instructions.map((instruction, idx) => (
                  <li key={idx} className="flex gap-3 items-start px-3 py-2.5 bg-[#F7F6F4] border border-[#D9D5D1] rounded-lg" style={{ counterIncrement: 's' }}>
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-[#231F20] text-white font-bold text-sm flex items-center justify-center" style={{ content: 'counter(s)' }}>
                      {idx + 1}
                    </span>
                    <span className="pt-0.5">{instruction}</span>
                  </li>
                ))}
              </ol>
            </section>
          </div>

          <div className="flex flex-col gap-5">
            {task.status === 'assigned' && (
              <section className="p-5 bg-white border border-[#D9D5D1] rounded-xl shadow-sm" aria-labelledby="act-h">
                <h2 id="act-h" className="text-base font-semibold mb-3">Acknowledge</h2>
                <div className="flex items-start gap-3 flex-wrap">
                  <button
                    onClick={handleAcknowledge}
                    disabled={acknowledging}
                    className="inline-flex items-center gap-2 min-h-11 px-4 rounded-lg font-semibold text-sm bg-[#E7002A] border-[#E7002A] text-white disabled:opacity-50"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="9"/>
                      <path d="m8 12 3 3 5-6"/>
                    </svg>
                    {acknowledging ? 'Acknowledging...' : 'Acknowledge task'}
                  </button>
                  <span className="text-[#68645F] text-sm max-w-xs">Acknowledging tells operations you have the task. Safe to retry: each action carries a unique client event ID.</span>
                </div>
              </section>
            )}

            <EvidenceForm
              taskId={task.task_id}
              taskStatus={task.status}
              onSubmit={handleEvidenceSubmit}
            />

            <section className="p-5 bg-white border border-[#D9D5D1] rounded-xl shadow-sm" aria-labelledby="hist-h">
              <h2 id="hist-h" className="text-base font-semibold mb-3">Evidence history</h2>
              {evidence.length === 0 ? (
                <p className="text-sm text-[#68645F]">No evidence recorded yet.</p>
              ) : (
                <table className="w-full text-sm" style={{ borderCollapse: 'collapse' }}>
                  <thead>
                    <tr>
                      <th className="text-left px-2.5 py-2 bg-[#EEECE9] text-[11.5px] tracking-wide uppercase text-[#68645F] border-b border-[#D9D5D1]" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>Time (GST)</th>
                      <th className="text-left px-2.5 py-2 bg-[#EEECE9] text-[11.5px] tracking-wide uppercase text-[#68645F] border-b border-[#D9D5D1]" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>Actor</th>
                      <th className="text-left px-2.5 py-2 bg-[#EEECE9] text-[11.5px] tracking-wide uppercase text-[#68645F] border-b border-[#D9D5D1]" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>Event</th>
                      <th className="text-left px-2.5 py-2 bg-[#EEECE9] text-[11.5px] tracking-wide uppercase text-[#68645F] border-b border-[#D9D5D1]" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>Summary</th>
                    </tr>
                  </thead>
                  <tbody>
                    {evidence.map((ev) => (
                      <tr key={ev.task_evidence_id}>
                        <td className="px-2.5 py-2.5 border-b border-[#D9D5D1] align-top">
                          {new Date(ev.recorded_at).toLocaleTimeString('en-GB', { timeZone: 'Asia/Dubai', hour: '2-digit', minute: '2-digit' })}
                        </td>
                        <td className="px-2.5 py-2.5 border-b border-[#D9D5D1] align-top">{ev.actor_display}</td>
                        <td className="px-2.5 py-2.5 border-b border-[#D9D5D1] align-top">{ev.event_type}</td>
                        <td className="px-2.5 py-2.5 border-b border-[#D9D5D1] align-top">{ev.evidence_summary}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </section>
          </div>
        </div>
      </main>

      <footer className="px-8 py-4 border-t border-[#D9D5D1] text-xs text-[#68645F] flex justify-between bg-white">
        <span>Data source: GET /api/v1/partner/tasks/{'{task_id}'} · POST /api/v1/partner/tasks/{'{task_id}'}/events</span>
        <span>Synthetic data · SIMULATED · Role-scoped view</span>
      </footer>
    </div>
  );
}
