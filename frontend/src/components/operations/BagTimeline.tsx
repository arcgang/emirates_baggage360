import { BagTimeline as BagTimelineType } from '../../types/operations';

interface BagTimelineProps {
  timelines: BagTimelineType[];
  activeBagId: string;
  onSelectBag: (bagId: string) => void;
}

const getFactTypeColor = (factType: string) => {
  switch (factType) {
    case 'observed':
      return 'bg-[#E3F4EC] text-[#18794E] border-[#9FD2B8]';
    case 'derived':
      return 'bg-[#E6F1FA] text-[#1769AA] border-[#A9CBE6]';
    case 'estimated':
      return 'bg-white text-[#A65A00] border border-dashed border-[#A65A00]';
    default:
      return 'bg-[#EEECE9] text-[#231F20] border-[#D9D5D1]';
  }
};

const getFreshnessColor = (freshness: string) => {
  switch (freshness) {
    case 'fresh':
      return 'bg-[#E3F4EC] text-[#18794E]';
    case 'stale':
      return 'bg-[#FFF1DE] text-[#A65A00]';
    default:
      return 'bg-[#FFF1DE] text-[#A65A00]';
  }
};

export default function BagTimeline({ timelines, activeBagId, onSelectBag }: BagTimelineProps) {
  const activeTimeline = timelines.find((t) => t.bag_id === activeBagId);

  return (
    <div className="bg-white border border-[#D9D5D1] rounded-xl shadow-sm p-5" aria-labelledby="tl-h">
      <h2 id="tl-h" className="text-base font-semibold mb-3">Bag timeline</h2>

      <div className="flex gap-1 border-b border-[#D9D5D1] mb-4" role="tablist" aria-label="Bags in case">
        {timelines.map((timeline) => (
          <button
            key={timeline.bag_id}
            role="tab"
            aria-current={activeBagId === timeline.bag_id ? 'true' : 'false'}
            onClick={() => onSelectBag(timeline.bag_id)}
            className={`inline-flex items-center h-9 px-3 font-semibold text-sm border-b-3 ${
              activeBagId === timeline.bag_id
                ? 'text-[#231F20] border-b-[#E7002A]'
                : 'text-[#68645F] border-b-transparent hover:text-[#231F20]'
            }`}
          >
            {timeline.bag_tag} {timeline === timelines[0] && '(focus)'}
          </button>
        ))}
      </div>

      {activeTimeline && (
        <ol className="space-y-4 border-l-2 border-[#D9D5D1] ml-2 pl-5" aria-label={`Milestones for ${activeTimeline.bag_tag}`}>
          {activeTimeline.milestones.map((milestone, index) => (
            <li key={index} className="relative">
              <div
                className={`absolute -left-7 top-1 w-3 h-3 rounded-full border-2 border-white ${
                  milestone.fact_type === 'observed'
                    ? 'bg-[#18794E] shadow-sm'
                    : milestone.fact_type === 'derived'
                    ? 'bg-white border-[#A65A00]'
                    : 'bg-white border-dashed border-[#A65A00]'
                }`}
              ></div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-bold">{milestone.event_type}</span>
                <span className={`inline-block px-1.5 py-0.5 text-[10.5px] font-bold tracking-wide border rounded ${getFactTypeColor(milestone.fact_type)}`}>
                  {milestone.fact_type.toUpperCase()}
                </span>
                {milestone.freshness_state !== 'fresh' && (
                  <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 text-xs font-semibold rounded-full ${getFreshnessColor(milestone.freshness_state)}`}>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="9"/>
                      <path d="M12 7v5l3 2"/>
                    </svg>
                    {milestone.freshness_state === 'stale' ? 'Stale' : 'Awaiting confirmation'}
                  </span>
                )}
              </div>
              <div className="text-xs text-[#68645F] mt-0.5">
                {new Date(milestone.observed_at).toLocaleString()} · {milestone.location_code || 'Unknown'} · source: {milestone.source_system}
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
