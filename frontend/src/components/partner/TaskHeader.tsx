import { PartnerTaskDetail } from '../../types/partner';

interface TaskHeaderProps {
  task: PartnerTaskDetail;
}

export default function TaskHeader({ task }: TaskHeaderProps) {
  const getDeadlineDisplay = (deadlineUtc: string) => {
    const deadline = new Date(deadlineUtc);
    const now = new Date();
    const minutesRemaining = Math.floor((deadline.getTime() - now.getTime()) / 60000);

    if (minutesRemaining < 0) {
      return {
        className: 'text-[#B42318]',
        icon: 'alert',
        label: `Overdue by ${Math.abs(minutesRemaining)} min`,
      };
    } else if (minutesRemaining < 30) {
      return {
        className: 'text-[#B42318]',
        icon: 'clock',
        label: `Due in ${minutesRemaining} min`,
      };
    } else if (minutesRemaining < 60) {
      return {
        className: 'text-[#B42318]',
        icon: 'alert',
        label: `Due in ${minutesRemaining} min`,
      };
    } else if (minutesRemaining < 90) {
      return {
        className: 'text-[#A65A00]',
        icon: 'clock',
        label: `Due in ${Math.floor(minutesRemaining / 60)} h ${minutesRemaining % 60} min`,
      };
    } else {
      return {
        className: '',
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
            Status: assigned
          </span>
        );
      case 'acknowledged':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#E3F4EC] text-[#18794E] border-[#9FD2B8]">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9"/>
              <path d="m8 12 3 3 5-6"/>
            </svg>
            Status: acknowledged
          </span>
        );
      case 'in_progress':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#FFF1DE] text-[#A65A00] border-[#E8C48F]">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9"/>
              <path d="M12 7v5l3 2"/>
            </svg>
            Status: in progress
          </span>
        );
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#E3F4EC] text-[#18794E] border-[#9FD2B8]">
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9"/>
              <path d="m8 12 3 3 5-6"/>
            </svg>
            Status: completed
          </span>
        );
      default:
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#EEECE9] text-[#231F20] border-[#D9D5D1]">Status: {status}</span>;
    }
  };

  const deadlineDisplay = getDeadlineDisplay(task.deadline_utc);

  return (
    <section className="bg-white border border-[#D9D5D1] rounded-xl shadow-sm p-5 flex items-center gap-4 flex-wrap" aria-labelledby="t-h">
      <div>
        <h1 id="t-h" className="text-[26px] font-semibold">{task.task_id} · Priority transfer</h1>
        <div className="flex gap-2 mt-2 flex-wrap">
          {getStatusChip(task.status)}
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#EEECE9] text-[#231F20] border-[#D9D5D1]">Station {task.station_code}</span>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border bg-[#EEECE9] text-[#231F20] border-[#D9D5D1]">Transfer Area</span>
        </div>
      </div>
      <div className="ml-auto text-right">
        <div className="text-xs font-bold tracking-wide text-[#68645F] mb-1" style={{ letterSpacing: '0.05em' }}>DEADLINE</div>
        <div className={`flex items-center gap-1.5 justify-end text-[26px] font-bold ${deadlineDisplay.className}`}>
          <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {deadlineDisplay.icon === 'alert' ? (
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
          {deadlineDisplay.label}
        </div>
        <div className="text-[#68645F]">{new Date(task.deadline_utc).toLocaleString('en-GB', { timeZone: 'Asia/Dubai', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}</div>
      </div>
    </section>
  );
}
