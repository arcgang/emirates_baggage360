/**
 * CaseStatusPage - Passenger delayed-bag case status with progress steps
 */
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiClient } from '../../lib/api-client';
import { PassengerCaseStatus } from '../../types/passenger';

export default function CaseStatusPage() {
  const { caseReference } = useParams<{ caseReference: string }>();
  const [caseStatus, setCaseStatus] = useState<PassengerCaseStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!caseReference) return;

    const fetchCaseStatus = async () => {
      try {
        setLoading(true);
        const data = await apiClient.get<PassengerCaseStatus>(
          `/passenger/cases/${caseReference}`
        );
        setCaseStatus(data);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to load case status'
        );
        setCaseStatus(null);
      } finally {
        setLoading(false);
      }
    };

    fetchCaseStatus();
  }, [caseReference]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <div className="rounded-lg border border-gray-300 bg-white p-6 shadow">
          <div className="mb-2 h-3 w-64 animate-pulse rounded bg-gray-200" />
          <div className="mb-2 h-3 w-48 animate-pulse rounded bg-gray-200" />
          <div className="h-3 w-56 animate-pulse rounded bg-gray-200" />
          <p className="mt-4 text-sm text-gray-500">Loading your case…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
        <div className="w-full max-w-md">
          <div
            className="mb-4 flex items-start gap-2 rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700"
            role="alert"
          >
            <svg
              className="h-5 w-5 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M12 3 2 20h20L12 3z" />
              <path d="M12 10v5M12 18v.5" />
            </svg>
            <span>
              We couldn't find that case reference. Check it and try again.
            </span>
          </div>
          <Link
            to="/login"
            className="inline-flex items-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
          >
            Back to sign in
          </Link>
        </div>
      </div>
    );
  }

  if (!caseStatus) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
        <div className="text-center">
          <p className="mb-4 text-gray-600">No case status available</p>
          <Link
            to="/login"
            className="inline-flex items-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
          >
            Back to sign in
          </Link>
        </div>
      </div>
    );
  }

  // Mock progress steps (in real implementation would come from caseStatus.progress_steps)
  const progressSteps = [
    {
      number: 1,
      label: 'Reported',
      details: 'Completed · 20:03 GST',
      status: 'done' as const,
    },
    {
      number: 2,
      label: 'Under review',
      details: 'Completed · 20:07 GST',
      status: 'done' as const,
    },
    {
      number: 3,
      label: 'Recovery in progress',
      details: 'We are moving your bag to your onward flight',
      status: 'current' as const,
    },
    {
      number: 4,
      label: 'Bag located and confirmed',
      details: 'Not yet. Comes after a confirmed scan',
      status: 'pending' as const,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-gray-900 px-4 py-2.5 text-white">
        <div className="flex items-center gap-2">
          <Link
            to="/passenger/bags/0176482193/status"
            className="flex h-11 w-11 -ml-2 items-center justify-center hover:bg-gray-800 rounded"
            aria-label="Back to bag status"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M19 12H5M11 6l-6 6 6 6" />
            </svg>
          </Link>
          <div className="flex flex-col leading-tight">
            <small className="text-xs text-gray-400">
              Baggage360 · Delayed-bag case
            </small>
            <strong className="text-base">{caseStatus.case_reference}</strong>
          </div>
          <span className="ml-auto rounded border border-orange-500 border-dashed bg-orange-100 px-2 py-0.5 text-xs font-bold tracking-wide text-orange-700">
            SIMULATED
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-md p-4">
        <div className="space-y-4">
          {/* Case Progress */}
          <section
            className="rounded-lg border border-gray-300 bg-white p-4 shadow-sm"
            aria-labelledby="case-progress"
          >
            <span className="mb-1 block text-xs font-bold uppercase tracking-wide text-gray-500">
              Case progress
            </span>
            <h1 id="case-progress" className="mb-3 text-xl font-bold leading-tight">
              We are working on your bag
            </h1>
            <ol className="flex flex-col gap-0" aria-label="Case progress, step 3 of 4 is current">
              {progressSteps.map((step, index) => (
                <li
                  key={step.number}
                  className="relative flex gap-3 pb-4 min-h-11"
                  style={
                    index === progressSteps.length - 1
                      ? {}
                      : {
                          borderLeft:
                            step.status === 'done'
                              ? '2px solid #16a34a'
                              : '2px solid #d1d5db',
                          marginLeft: '11px',
                        }
                  }
                >
                  <span
                    className={`flex h-6 w-6 items-center justify-center rounded-full border-2 text-xs font-bold ${
                      step.status === 'done'
                        ? 'border-green-600 bg-green-600 text-white'
                        : step.status === 'current'
                        ? 'border-gray-900 bg-gray-900 text-white shadow-[0_0_0_4px_#d1d5db]'
                        : 'border-gray-500 bg-white text-gray-500'
                    }`}
                    aria-hidden="true"
                  >
                    {step.status === 'done' ? '✓' : step.number}
                  </span>
                  <div>
                    <div className="font-bold">
                      {step.label}
                      {step.status === 'current' && (
                        <span className="ml-2 inline-flex items-center gap-1 rounded-full border border-blue-600 bg-blue-100 px-2 py-0.5 text-xs font-semibold text-blue-700">
                          Current step
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600">{step.details}</div>
                  </div>
                </li>
              ))}
            </ol>
          </section>

          {/* Latest Confirmed Status */}
          <section
            className="rounded-lg border border-gray-300 bg-white p-4 shadow-sm"
            aria-labelledby="latest-confirmed"
          >
            <span className="mb-1 block text-xs font-bold uppercase tracking-wide text-gray-500">
              Latest confirmed status
            </span>
            <h2 id="latest-confirmed" className="mb-1 flex items-center gap-2 text-lg font-bold">
              <svg
                className="h-5 w-5 text-green-600"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="9" />
                <path d="m8 12 3 3 5-6" />
              </svg>
              {caseStatus.latest_confirmed_status}
            </h2>
            <div className="mt-2">
              <span className="inline-flex items-center gap-1 rounded-full border border-green-600 bg-green-100 px-2.5 py-0.5 text-xs font-semibold text-green-700">
                <svg
                  className="h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="9" />
                  <path d="m8 12 3 3 5-6" />
                </svg>
                Confirmed
              </span>
            </div>
          </section>

          {/* Estimated Update */}
          {caseStatus.estimated_notice && (
            <section
              className="rounded-lg border-2 border-dashed border-orange-500 bg-orange-50 p-4"
              aria-labelledby="estimated-update"
            >
              <span className="mb-2 inline-flex items-center gap-1 rounded-full border border-orange-500 border-dashed bg-orange-100 px-2.5 py-0.5 text-xs font-semibold text-orange-700">
                <svg
                  className="h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="9" />
                  <path d="M12 11v6M12 7.5v.5" />
                </svg>
                Estimated
              </span>
              <h2 id="estimated-update" className="mb-1 text-lg font-bold">
                Estimated update
              </h2>
              <p className="text-sm">{caseStatus.estimated_notice}</p>
              <p className="mt-2 text-xs text-gray-600">
                Why it is uncertain: your inbound flight was late, so we are working
                to move your bag onto your next flight. We will confirm once it has
                been scanned.
              </p>
            </section>
          )}

          {/* Next Expected Update */}
          <div className="flex items-center gap-2 rounded-lg border border-gray-300 bg-white p-3 shadow-sm">
            <svg
              className="h-5 w-5 flex-shrink-0 text-blue-600"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="9" />
              <path d="M12 7v5l3 2" />
            </svg>
            <div>
              <strong className="block text-sm">
                Next expected update {caseStatus.next_expected_update}
              </strong>
              <span className="text-xs text-gray-600">
                Last updated{' '}
                {new Date(caseStatus.last_updated_at).toLocaleTimeString('en-US', {
                  hour: '2-digit',
                  minute: '2-digit',
                  timeZone: 'Asia/Dubai',
                  timeZoneName: 'short',
                })}
              </span>
            </div>
          </div>

          {/* What This Means */}
          <section
            className="rounded-lg border border-gray-300 bg-white p-4 shadow-sm"
            aria-labelledby="what-this-means"
          >
            <h2 id="what-this-means" className="mb-1 text-lg font-bold">
              What this means for you
            </h2>
            <ul className="space-y-2">
              <li className="flex gap-2.5 border-b border-gray-200 py-2">
                <svg
                  className="h-5 w-5 flex-shrink-0 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="9" />
                  <path d="m8 12 3 3 5-6" />
                </svg>
                <span className="text-sm">Nothing you need to do right now.</span>
              </li>
              <li className="flex gap-2.5 border-b border-gray-200 py-2">
                <svg
                  className="h-5 w-5 flex-shrink-0 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="9" />
                  <path d="M12 11v6M12 7.5v.5" />
                </svg>
                <span className="text-sm">
                  We'll update this page as soon as there is a confirmed scan.
                </span>
              </li>
              <li className="flex gap-2.5 py-2">
                <svg
                  className="h-5 w-5 flex-shrink-0 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="9" />
                  <path d="M12 7v5l3 2" />
                </svg>
                <span className="text-sm">
                  Times shown are Dubai local time (GST, UTC+4).
                </span>
              </li>
            </ul>
          </section>

          {/* Back to Bag Status */}
          <Link
            to="/passenger/bags/0176482193/status"
            className="flex items-center justify-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M19 12H5M11 6l-6 6 6 6" />
            </svg>
            Back to bag status
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-8 border-t border-gray-300 bg-white px-4 py-4 text-xs text-gray-600">
        <Link to="/login" className="font-semibold hover:underline">
          Sign out
        </Link>
        <br />
        Demo with synthetic data. Not a live Emirates service.
        <br />
        Data source: GET /api/v1/passenger/cases/{caseReference}
      </footer>
    </div>
  );
}
