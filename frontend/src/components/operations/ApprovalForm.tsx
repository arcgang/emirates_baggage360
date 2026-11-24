import { useState, FormEvent } from 'react';
import { ApprovalDecisionRequest } from '../../types/operations';

interface ApprovalFormProps {
  recommendationId: string;
  recommendationLabel: string;
  onSubmit: (request: ApprovalDecisionRequest) => Promise<void>;
  isSubmitting?: boolean;
}

export default function ApprovalForm({
  recommendationId,
  recommendationLabel,
  onSubmit,
  isSubmitting = false,
}: ApprovalFormProps) {
  const [decision, setDecision] = useState<'approve' | 'reject'>('approve');
  const [rationale, setRationale] = useState('Connection window critical, expedite approved');
  const [showConfirm, setShowConfirm] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!rationale.trim()) {
      return;
    }

    if (!showConfirm) {
      setShowConfirm(true);
      return;
    }

    try {
      await onSubmit({
        recommendation_id: recommendationId,
        decision,
        rationale: rationale.trim(),
      });
      setShowConfirm(false);
    } catch (error) {
      console.error('Approval submission failed:', error);
      setShowConfirm(false);
    }
  };

  return (
    <section className="bg-white border border-[#D9D5D1] rounded-xl shadow-sm p-5" aria-labelledby="ap-h">
      <h2 id="ap-h" className="text-base font-semibold mb-3">Approval decision</h2>

      <div className="flex gap-2 items-start p-3 rounded-lg bg-[#E6F1FA] text-[#1769AA] border border-[#A9CBE6] mb-4">
        <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="5" y="11" width="14" height="9" rx="2"/>
          <path d="M8 11V8a4 4 0 0 1 8 0v3"/>
        </svg>
        <span className="text-sm">
          <strong>No task is dispatched until approved.</strong> Your decision and rationale are recorded in the audit trail.
        </span>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="dec" className="block font-semibold text-sm mb-2">Decision</label>
          <select
            id="dec"
            value={decision}
            onChange={(e) => setDecision(e.target.value as 'approve' | 'reject')}
            className="w-full h-11 px-3 border border-[#8A857F] rounded-lg"
            disabled={isSubmitting}
          >
            <option value="approve">Approve {recommendationLabel}</option>
            <option value="reject">Reject {recommendationLabel}</option>
          </select>
        </div>

        <div className="mb-4">
          <label htmlFor="rat" className="block font-semibold text-sm mb-2">Rationale (required)</label>
          <textarea
            id="rat"
            value={rationale}
            onChange={(e) => setRationale(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-[#8A857F] rounded-lg resize-none"
            disabled={isSubmitting}
            required
          />
        </div>

        {showConfirm && (
          <div className="border-2 border-[#231F20] rounded-xl p-4 bg-white mb-4">
            <strong className="block mb-1">Confirm {decision === 'approve' ? 'approval' : 'rejection'} of {recommendationLabel}?</strong>
            <p className="text-[#68645F] text-sm mb-3">
              {decision === 'approve'
                ? 'This creates a task for the assigned partner.'
                : 'No task will be dispatched.'}
            </p>
            <div className="flex gap-2">
              <button
                type="submit"
                className="h-8 px-3 bg-[#E7002A] text-white font-semibold rounded text-sm"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : 'Confirm'}
              </button>
              <button
                type="button"
                onClick={() => setShowConfirm(false)}
                className="h-8 px-3 bg-white border border-[#D9D5D1] font-semibold rounded text-sm"
                disabled={isSubmitting}
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {!showConfirm && (
          <div>
            <button
              type="submit"
              disabled={isSubmitting || !rationale.trim()}
              className="h-11 px-4 bg-[#E7002A] text-white font-semibold rounded-lg flex items-center gap-2 disabled:opacity-50"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="9"/>
                <path d="m8 12 3 3 5-6"/>
              </svg>
              Approve and dispatch tasks
            </button>
            <p className="text-xs text-[#68645F] mt-2">
              Dispatch creates a task for the Handler Supervisor, Transfer Area, DXB. The task is visible to the partner role only.
            </p>
          </div>
        )}
      </form>
    </section>
  );
}
