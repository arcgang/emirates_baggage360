import { Link } from 'react-router-dom';
import { PartnerTaskCard } from '../../types/partner';
import { formatRelativeTime } from '../../lib/utils';

interface TaskTableProps {
  tasks: PartnerTaskCard[];
  loading?: boolean;
}

export default function TaskTable({ tasks, loading }: TaskTableProps) {
  if (loading) {
    return (
      <div className="p-5 text-center text-sm text-[#68645F]">
        <div className="mb-2 text-base">Loading your tasks…</div>
        <div className="space-y-2">
          <div className="h-3 bg-[#EEECE9] rounded w-3/4 mx-auto"></div>
          <div className="h-3 bg-[#EEECE9] rounded w-2/3 mx-auto"></div>
          <div className="h-3 bg-[#EEECE9] rounded w-5/6 mx-auto"></div>
        </div>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="p-8 text-center">
        <strong className="block text-sm font-semibold mb-2">No tasks assigned right now</strong>
        <span className="text-xs text-[#68645F]">New tasks appear here when an operations lead approves an action for your role.</span>
      </div>
    );
  }

  const getDeadlineEmphasis = (deadlineUtc: string) => {
    const deadline = new Date(deadlineUtc);
    const now = new Date();
    const minutesRemaining = Math.floor((deadline.getTime() - now.getTime()) / 60000);

    if (minutesRemaining < 0) {
      return {
        className: 'text-[#B42318] font-bold flex items-center gap-1',
        icon: 'alert',
        label: `Overdue by ${Math.abs(minutesRemaining)} min`,
      };
    } else if (minutesRemaining < 30) {
      return {
        className: 'text-[#B42318] font-bold flex items-center gap-1',
        icon: 'clock',
        label: `Due in ${minutesRemaining} min`,
      };
    } else if (minutesRemaining < 60) {
      return {
        className: 'text-[#B42318] font-bold flex items-center gap-1',
        icon: 'alert',
        label: `Due in ${minutesRemaining} min · near deadline`,
      };
    } else if (minutesRemaining < 90) {
      return {
        className: 'text-[#A65A00] font-bold flex items-center gap-1',
        icon: 'clock',
        label: `Due in ${Math.floor(minutesRemaining / 60)} h ${minutesRemaining % 60} min`,
      };
    } else {
      return {
        className: 'flex items-center gap-1',
        icon: 'clock',
        label: `Due in ${Math.floor(minutesRemaining / 60)} h ${minutesRemaining % 60} min`,
      };
    }
  };

  const getStatusChip = (status: string) => {
    switch (status) {
      case 'assigned':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#E6F1FA] text-[#1769AA] border-[#A9CBE6]">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9"/>
              <path d="M12 11v6M12 7.5v.5"/>
            </svg>
            Assigned
          </span>
        );
      case 'acknowledged':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#E3F4EC] text-[#18794E] border-[#9FD2B8]">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9"/>
              <path d="m8 12 3 3 5-6"/>
            </svg>
            Acknowledged
          </span>
        );
      case 'in_progress':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#FFF1DE] text-[#A65A00] border-[#E8C48F]">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9"/>
              <path d="M12 7v5l3 2"/>
            </svg>
            In progress
          </span>
        );
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#E3F4EC] text-[#18794E] border-[#9FD2B8]">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9"/>
              <path d="m8 12 3 3 5-6"/>
            </svg>
            Completed
          </span>
        );
      default:
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#EEECE9] text-[#231F20] border-[#D9D5D1]">{status}</span>;
    }
  };

  return (
    <table className="w-full text-[13.5px]" style={{ borderCollapse: 'collapse' }}>
      <thead>
        <tr>
          <th className="text-left px-3.5 py-3 bg-[#EEECE9] text-[11.5px] tracking-wide uppercase text-[#68645F] border-b border-[#D9D5D1]" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>Task</th>
          <th className="text-left px-3.5 py-3 bg-[#EEECE9] text-[11.5px] tracking-wide uppercase text-[#68645F] border-b border-[#D9D5D1]" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>Bag reference</th>
          <th className="text-left px-3.5 py-3 bg-[#EEECE9] text-[11.5px] tracking-wide uppercase text-[#68645F] border-b border-[#D9D5D1]" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>Flight context</th>
          <th className="text-left px-3.5 py-3 bg-[#EEECE9] text-[11.5px] tracking-wide uppercase text-[#68645F] border-b border-[#D9D5D1]" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>Station</th>
          <th className="text-left px-3.5 py-3 bg-[#EEECE9] text-[11.5px] tracking-wide uppercase text-[#68645F] border-b border-[#D9D5D1]" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>Deadline</th>
          <th className="text-left px-3.5 py-3 bg-[#EEECE9] text-[11.5px] tracking-wide uppercase text-[#68645F] border-b border-[#D9D5D1]" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>Status</th>
          <th className="text-left px-3.5 py-3 bg-[#EEECE9] text-[11.5px] tracking-wide uppercase text-[#68645F] border-b border-[#D9D5D1]" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>Instruction summary</th>
          <th className="text-left px-3.5 py-3 bg-[#EEECE9] text-[11.5px] tracking-wide uppercase text-[#68645F] border-b border-[#D9D5D1]" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>Action</th>
        </tr>
      </thead>
      <tbody>
        {tasks.map((task, idx) => {
          const deadlineEmphasis = getDeadlineEmphasis(task.deadline_utc);
          const isFirst = idx === 0;
          
          return (
            <tr key={task.task_id} className={isFirst ? 'bg-[#FBF3F4]' : ''}>
              <td className={`px-3.5 py-3.5 border-b border-[#D9D5D1] align-top ${isFirst ? 'border-l-4 border-l-[#E7002A]' : ''}`} style={{ fontWeight: 700 }}>{task.task_id}</td>
              <td className="px-3.5 py-3.5 border-b border-[#D9D5D1] align-top">{task.bag_reference}</td>
              <td className="px-3.5 py-3.5 border-b border-[#D9D5D1] align-top">
                <div dangerouslySetInnerHTML={{ __html: task.flight_context.replace(/\n/g, '<br/>') }} />
              </td>
              <td className="px-3.5 py-3.5 border-b border-[#D9D5D1] align-top">{task.station_code}</td>
              <td className="px-3.5 py-3.5 border-b border-[#D9D5D1] align-top">
                <div className={deadlineEmphasis.className}>
                  <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    {deadlineEmphasis.icon === 'alert' ? (
                      <>
                        <path d="M12 3 2 20h20L12 3z"/>
                        <path d="M12 10v5M12 18v.5"/>
                      </>
                    ) : (
                      <>
                        <circle cx="12" cy="12" r="9"/>
                        <path d="M12 7v5l3 2"/>
                      </>
                    )}
                  </svg>
                  {deadlineEmphasis.label}
                </div>
                <div className="text-xs text-[#68645F] mt-1">{new Date(task.deadline_utc).toLocaleString('en-GB', { timeZone: 'Asia/Dubai', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}</div>
              </td>
              <td className="px-3.5 py-3.5 border-b border-[#D9D5D1] align-top">{getStatusChip(task.status)}</td>
              <td className="px-3.5 py-3.5 border-b border-[#D9D5D1] align-top">{task.instruction_summary}</td>
              <td className="px-3.5 py-3.5 border-b border-[#D9D5D1] align-top">
                <Link
                  to={`/partner/tasks/${task.task_id}`}
                  className={`inline-flex items-center justify-center gap-2 min-h-9 px-3 rounded-lg font-semibold text-sm border ${
                    isFirst ? 'bg-[#E7002A] border-[#E7002A] text-white' : 'bg-white border-[#D9D5D1] text-[#231F20]'
                  }`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M13 6l6 6-6 6"/>
                  </svg>
                  Open task
                </Link>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
