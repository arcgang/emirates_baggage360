import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import TaskTable from '../../components/partner/TaskTable';
import { PartnerTaskCard, PartnerTaskQueueResponse } from '../../types/partner';
import { apiClient } from '../../lib/api-client';

type StatusFilter = 'assigned' | 'acknowledged' | 'in_progress' | 'completed' | null;

export default function TaskQueuePage() {
  const [tasks, setTasks] = useState<PartnerTaskCard[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<PartnerTaskCard[]>([]);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('assigned');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshError, setRefreshError] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const loadTasks = async () => {
    setLoading(true);
    setError('');
    setRefreshError(false);
    
    try {
      const response = await apiClient.get<PartnerTaskQueueResponse>('/partner/tasks');
      const data = Array.isArray(response) ? { items: response, total: response.length, generated_at: new Date().toISOString() } : response;
      setTasks(data.items || []);
      setLastUpdated(new Date(data.generated_at));
      filterTasks(data.items || [], statusFilter);
    } catch (err) {
      if (err instanceof Error && err.message.includes('403')) {
        setError('Your role cannot open this task. Only tasks assigned to your role and station are available.');
      } else {
        setRefreshError(true);
        setError('Your tasks could not be refreshed. The list below may be out of date.');
      }
    } finally {
      setLoading(false);
    }
  };

  const filterTasks = (allTasks: PartnerTaskCard[], filter: StatusFilter) => {
    if (!filter) {
      setFilteredTasks(allTasks);
    } else {
      setFilteredTasks(allTasks.filter(t => t.status === filter));
    }
  };

  useEffect(() => {
    loadTasks();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    filterTasks(tasks, statusFilter);
  }, [statusFilter, tasks]);

  const getStatusCount = (status: string) => {
    return tasks.filter(t => t.status === status).length;
  };

  const handleRefresh = () => {
    loadTasks();
  };

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
          <Link
            to="/partner/tasks"
            aria-current="page"
            className="inline-flex items-center min-h-16 px-2 text-white font-semibold border-b-4 border-b-[#E7002A]"
          >
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
      <main id="main" className="p-8 flex flex-col gap-5">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-[28px] font-semibold">My tasks</h1>
            <p className="text-[#68645F]">
              Station DXB · Transfer Area · Last updated {lastUpdated.toLocaleTimeString('en-GB', { timeZone: 'Asia/Dubai', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}{' '}
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#E3F4EC] text-[#18794E] border-[#9FD2B8] ml-1.5">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="9"/>
                  <path d="m8 12 3 3 5-6"/>
                </svg>
                Fresh {Math.floor((Date.now() - lastUpdated.getTime()) / 60000)} min
              </span>
            </p>
          </div>
          <button
            onClick={handleRefresh}
            className="inline-flex items-center gap-2 min-h-11 px-4 rounded-lg font-semibold text-sm border border-[#D9D5D1] bg-white"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 11a8 8 0 0 0-14-4M4 4v4h4M4 13a8 8 0 0 0 14 4M20 20v-4h-4"/>
            </svg>
            Refresh
          </button>
        </div>

        <div className="flex gap-2.5 items-center px-4 py-3 bg-[#E6F1FA] border border-[#A9CBE6] rounded-lg text-[#0F4C7A]" role="note">
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
          <span><strong>You see only tasks assigned to your role.</strong> Passenger details are masked. Risk scores and other cases are not shown.</span>
        </div>

        {error && !refreshError && (
          <div className="flex gap-2 items-start p-3 rounded-lg bg-[#FDE9E7] text-[#B42318] border border-[#E9B4AE]" role="alert">
            <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="5" y="11" width="14" height="9" rx="2"/>
              <path d="M8 11V8a4 4 0 0 1 8 0v3"/>
            </svg>
            <span>{error}</span>
          </div>
        )}

        {refreshError && (
          <div className="flex gap-2 items-start p-3 rounded-lg bg-[#FDE9E7] text-[#B42318] border border-[#E9B4AE]" role="alert">
            <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 3 2 20h20L12 3z"/>
              <path d="M12 10v5M12 18v.5"/>
            </svg>
            <span>{error}</span>
            <button
              onClick={handleRefresh}
              className="ml-auto inline-flex items-center gap-2 min-h-9 px-3 rounded-lg font-semibold text-sm border border-[#D9D5D1] bg-white"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 11a8 8 0 0 0-14-4M4 4v4h4M4 13a8 8 0 0 0 14 4M20 20v-4h-4"/>
              </svg>
              Retry
            </button>
          </div>
        )}

        <section className="bg-white border border-[#D9D5D1] rounded-xl shadow-sm" aria-labelledby="list-h">
          <h2 id="list-h" className="px-4 pt-4 text-base font-semibold">Task list, ordered by deadline</h2>
          <div className="flex gap-1 px-4 border-b border-[#D9D5D1]" role="tablist" aria-label="Task status filter">
            <button
              role="tab"
              aria-current={statusFilter === 'assigned' ? 'true' : undefined}
              onClick={() => setStatusFilter('assigned')}
              className={`inline-flex items-center gap-2 min-h-11 px-4 font-semibold border-b-3 ${
                statusFilter === 'assigned' ? 'text-[#231F20] border-b-[#E7002A]' : 'text-[#68645F] border-b-transparent'
              }`}
            >
              Assigned <span className="inline-flex items-center justify-center min-w-6 h-5 px-2 bg-[#EEECE9] text-[#231F20] text-xs font-semibold rounded-full">{getStatusCount('assigned')}</span>
            </button>
            <button
              role="tab"
              aria-current={statusFilter === 'acknowledged' ? 'true' : undefined}
              onClick={() => setStatusFilter('acknowledged')}
              className={`inline-flex items-center gap-2 min-h-11 px-4 font-semibold border-b-3 ${
                statusFilter === 'acknowledged' ? 'text-[#231F20] border-b-[#E7002A]' : 'text-[#68645F] border-b-transparent'
              }`}
            >
              Acknowledged <span className="inline-flex items-center justify-center min-w-6 h-5 px-2 bg-[#EEECE9] text-[#231F20] text-xs font-semibold rounded-full">{getStatusCount('acknowledged')}</span>
            </button>
            <button
              role="tab"
              aria-current={statusFilter === 'in_progress' ? 'true' : undefined}
              onClick={() => setStatusFilter('in_progress')}
              className={`inline-flex items-center gap-2 min-h-11 px-4 font-semibold border-b-3 ${
                statusFilter === 'in_progress' ? 'text-[#231F20] border-b-[#E7002A]' : 'text-[#68645F] border-b-transparent'
              }`}
            >
              In progress <span className="inline-flex items-center justify-center min-w-6 h-5 px-2 bg-[#EEECE9] text-[#231F20] text-xs font-semibold rounded-full">{getStatusCount('in_progress')}</span>
            </button>
            <button
              role="tab"
              aria-current={statusFilter === 'completed' ? 'true' : undefined}
              onClick={() => setStatusFilter('completed')}
              className={`inline-flex items-center gap-2 min-h-11 px-4 font-semibold border-b-3 ${
                statusFilter === 'completed' ? 'text-[#231F20] border-b-[#E7002A]' : 'text-[#68645F] border-b-transparent'
              }`}
            >
              Completed <span className="inline-flex items-center justify-center min-w-6 h-5 px-2 bg-[#EEECE9] text-[#231F20] text-xs font-semibold rounded-full">{getStatusCount('completed')}</span>
            </button>
          </div>

          <TaskTable tasks={filteredTasks} loading={loading} />

          <div className="flex justify-between items-center px-4 py-3 border-t border-[#D9D5D1] text-xs text-[#68645F]">
            <span>Showing {filteredTasks.length} of {tasks.length} tasks assigned to your role today</span>
            <span>Times shown in GST (UTC+4)</span>
          </div>
        </section>
      </main>

      <footer className="px-8 py-4 border-t border-[#D9D5D1] text-xs text-[#68645F] flex justify-between bg-white">
        <span>Data source: GET /api/v1/partner/tasks?status={statusFilter || 'all'}</span>
        <span>Synthetic data · SIMULATED · Passenger details masked for your role</span>
      </footer>
    </div>
  );
}
