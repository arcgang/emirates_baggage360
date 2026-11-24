import { Recommendation } from '../../types/operations';

interface RecommendationCardProps {
  recommendation: Recommendation;
  isTop?: boolean;
}

export default function RecommendationCard({ recommendation, isTop }: RecommendationCardProps) {
  return (
    <article
      className={`p-4 rounded-lg bg-white ${
        isTop ? 'border-2 border-[#231F20]' : 'border border-[#D9D5D1]'
      }`}
      aria-labelledby={`rec-${recommendation.recommendation_id}`}
    >
      <div className="flex justify-between items-center mb-2">
        <h3 id={`rec-${recommendation.recommendation_id}`} className="text-[15px] font-semibold">
          {recommendation.action_label}
        </h3>
        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-[#EEECE9] text-[#231F20] text-xs font-semibold rounded-full border border-[#D9D5D1]">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="5" y="11" width="14" height="9" rx="2"/>
            <path d="M8 11V8a4 4 0 0 1 8 0v3"/>
          </svg>
          Requires approval
        </span>
      </div>

      <div className="flex gap-4 my-2 text-sm">
        <span>
          Confidence <strong>{recommendation.confidence_score.toFixed(2)}</strong>
        </span>
        <span>
          Freshness <strong>{recommendation.freshness_state}</strong>
        </span>
        <span>
          Evidence <strong>{recommendation.evidence.length} items</strong>
        </span>
      </div>

      <p className="text-sm mb-2">{recommendation.reason_text}</p>

      {recommendation.evidence.length > 0 && (
        <ul className="space-y-1 text-sm text-[#68645F]" aria-label="Evidence">
          {recommendation.evidence.map((item, index) => (
            <li key={index} className="pl-4 relative">
              <span className="absolute left-1 top-2 w-1.5 h-1.5 bg-[#68645F] rounded-full"></span>
              {item}
            </li>
          ))}
        </ul>
      )}
    </article>
  );
}
