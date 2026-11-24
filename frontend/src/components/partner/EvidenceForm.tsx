import { useState } from 'react';
import { TaskEventRequest } from '../../types/partner';

interface EvidenceFormProps {
  taskId: string;
  taskStatus: string;
  onSubmit: (event: TaskEventRequest) => Promise<void>;
  disabled?: boolean;
}

export default function EvidenceForm({ taskId, taskStatus, onSubmit, disabled }: EvidenceFormProps) {
  const [eventType, setEventType] = useState<'in_progress' | 'completed'>('in_progress');
  const [evidenceType, setEvidenceType] = useState<'scan_confirmation' | 'handover_proof' | 'completion_note'>('scan_confirmation');
  const [evidenceReference, setEvidenceReference] = useState('');
  const [note, setNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async () => {
    setError('');
    setSuccess('');

    // Validation
    if (!evidenceReference.trim()) {
      setError('Enter an evidence reference before submitting.');
      return;
    }

    setIsSubmitting(true);

    try {
      const clientEventId = `CLIENT-EVT-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      await onSubmit({
        event_type: eventType,
        client_event_id: clientEventId,
        note: note.trim() || undefined,
        evidence_type: evidenceType,
        evidence_reference: evidenceReference.trim(),
      });
      setSuccess(`Evidence submitted at ${new Date().toLocaleTimeString('en-GB', { timeZone: 'Asia/Dubai', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}. Case updated.`);
      // Reset form
      setEvidenceReference('');
      setNote('');
    } catch (err) {
      if (err instanceof Error) {
        setError(`Evidence was not sent. ${err.message}. Check your connection and retry. Retrying will not create a duplicate.`);
      } else {
        setError('Evidence was not sent. Check your connection and retry. Retrying will not create a duplicate.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (taskStatus === 'completed') {
    return (
      <div className="p-5 bg-white border border-[#D9D5D1] rounded-xl shadow-sm">
        <h2 className="text-base font-semibold mb-3">Record evidence</h2>
        <div className="flex gap-2 items-start p-3 rounded-lg bg-[#E3F4EC] text-[#18794E] border border-[#9FD2B8] text-sm">
          <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="9"/>
            <path d="m8 12 3 3 5-6"/>
          </svg>
          <span><strong>Task completed.</strong> All fields are read-only. Evidence history remains visible.</span>
        </div>
      </div>
    );
  }

  if (taskStatus === 'assigned') {
    return (
      <div className="p-5 bg-white border border-[#D9D5D1] rounded-xl shadow-sm">
        <h2 className="text-base font-semibold mb-3">Record evidence</h2>
        <div className="flex gap-2 items-start p-3 rounded-lg bg-[#E6F1FA] text-[#1769AA] border border-[#A9CBE6] text-sm">
          <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="9"/>
            <path d="M12 11v6M12 7.5v.5"/>
          </svg>
          <span>Enabled after you acknowledge. Shown here as it appears once acknowledged.</span>
        </div>
        <div className="mt-4 opacity-50 pointer-events-none">
          <div className="mb-3">
            <label className="block font-semibold text-sm mb-1.5">Event type</label>
            <div className="flex items-center justify-between min-h-11 px-3 border border-[#8A857F] rounded-lg bg-white">
              <span>In progress</span>
              <span aria-hidden="true">▾</span>
            </div>
          </div>
          <div className="mb-3">
            <label className="block font-semibold text-sm mb-1.5">Evidence type</label>
            <div className="flex items-center justify-between min-h-11 px-3 border border-[#8A857F] rounded-lg bg-white">
              <span>Scan confirmation</span>
              <span aria-hidden="true">▾</span>
            </div>
          </div>
          <div className="mb-3">
            <label className="block font-semibold text-sm mb-1.5">Evidence reference</label>
            <div className="flex items-center justify-between min-h-11 px-3 border border-[#8A857F] rounded-lg bg-white">
              <span className="text-[#68645F]">SCAN-DXB-TA-0176482193-2014</span>
            </div>
          </div>
          <div className="mb-3">
            <label className="block font-semibold text-sm mb-1.5">Note (optional)</label>
            <div className="min-h-20 px-3 py-2 border border-[#8A857F] rounded-lg bg-white text-[#68645F]">
              Bags located at transfer area lane 2. Moving to priority belt now.
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-5 bg-white border border-[#D9D5D1] rounded-xl shadow-sm">
      <h2 id="ev-h" className="text-base font-semibold mb-3">Record evidence</h2>

      {error && (
        <div className="flex gap-2 items-start p-3 rounded-lg bg-[#FFF1DE] text-[#A65A00] border border-[#E8C48F] text-sm mb-3" role="alert">
          <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 3 2 20h20L12 3z"/>
            <path d="M12 10v5M12 18v.5"/>
          </svg>
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="flex gap-2 items-start p-3 rounded-lg bg-[#E3F4EC] text-[#18794E] border border-[#9FD2B8] text-sm mb-3" role="status">
          <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="9"/>
            <path d="m8 12 3 3 5-6"/>
          </svg>
          <span>{success}</span>
        </div>
      )}

      <div className="mb-3">
        <label htmlFor="et" className="block font-semibold text-sm mb-1.5">Event type</label>
        <select
          id="et"
          value={eventType}
          onChange={(e) => setEventType(e.target.value as 'in_progress' | 'completed')}
          disabled={disabled || isSubmitting}
          className="w-full min-h-11 px-3 border border-[#8A857F] rounded-lg bg-white"
        >
          <option value="in_progress">In progress</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      <div className="mb-3">
        <label htmlFor="ety" className="block font-semibold text-sm mb-1.5">Evidence type</label>
        <select
          id="ety"
          value={evidenceType}
          onChange={(e) => setEvidenceType(e.target.value as 'scan_confirmation' | 'handover_proof' | 'completion_note')}
          disabled={disabled || isSubmitting}
          className="w-full min-h-11 px-3 border border-[#8A857F] rounded-lg bg-white"
        >
          <option value="scan_confirmation">Scan confirmation</option>
          <option value="handover_proof">Handover proof</option>
          <option value="completion_note">Completion note</option>
        </select>
      </div>

      <div className="mb-3">
        <label htmlFor="er" className="block font-semibold text-sm mb-1.5">Evidence reference</label>
        <input
          id="er"
          type="text"
          value={evidenceReference}
          onChange={(e) => setEvidenceReference(e.target.value)}
          disabled={disabled || isSubmitting}
          className={`w-full min-h-11 px-3 border rounded-lg bg-white ${error && !evidenceReference.trim() ? 'border-2 border-[#B42318]' : 'border-[#8A857F]'}`}
          placeholder="SCAN-DXB-TA-0176482193-2014"
        />
      </div>

      <div className="mb-3">
        <label htmlFor="en" className="block font-semibold text-sm mb-1.5">Note (optional)</label>
        <textarea
          id="en"
          value={note}
          onChange={(e) => setNote(e.target.value)}
          disabled={disabled || isSubmitting}
          maxLength={1000}
          rows={3}
          className="w-full px-3 py-2 border border-[#8A857F] rounded-lg bg-white resize-none"
          placeholder="Bags located at transfer area lane 2. Moving to priority belt now."
        />
        <div className="text-xs text-[#68645F] text-right mt-0.5">{note.length} / 1000 characters</div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={disabled || isSubmitting}
        className="inline-flex items-center justify-center gap-2 min-h-11 px-4 rounded-lg font-semibold text-sm bg-[#231F20] border-[#231F20] text-white disabled:opacity-50"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7z"/>
        </svg>
        {isSubmitting ? 'Submitting...' : 'Submit evidence'}
      </button>
      <p className="text-xs text-[#68645F] mt-2">Submitting updates the case for the operations team. Your name, time and evidence reference are recorded in the audit trail.</p>
    </div>
  );
}
