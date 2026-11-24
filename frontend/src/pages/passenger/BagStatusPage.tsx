/**
 * BagStatusPage - Passenger bag status with confirmed milestones and estimated next step
 */
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiClient } from '../../lib/api-client';
import { PassengerBagStatus } from '../../types/passenger';
import StatusHeadline from '../../components/passenger/StatusHeadline';
import BagJourney from '../../components/passenger/BagJourney';

export default function BagStatusPage() {
  const { bagTag } = useParams<{ bagTag: string }>();
  const [status, setStatus] = useState<PassengerBagStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!bagTag) return;

    const fetchStatus = async () => {
      try {
        setLoading(true);
        const data = await apiClient.get<PassengerBagStatus>(
          `/passenger/bags/${bagTag}/status`
        );
        setStatus(data);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to load bag status'
        );
        setStatus(null);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, [bagTag]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <div className="rounded-lg border border-gray-300 bg-white p-6 shadow">
          <div className="mb-2 h-3 w-64 animate-pulse rounded bg-gray-200" />
          <div className="mb-2 h-3 w-48 animate-pulse rounded bg-gray-200" />
          <div className="h-3 w-56 animate-pulse rounded bg-gray-200" />
          <p className="mt-4 text-sm text-gray-500">Checking your bag status…</p>
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
            <span>We couldn't find that bag. Check the tag number and try again.</span>
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

  if (!status) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
        <div className="text-center">
          <p className="mb-4 text-gray-600">No bag status available</p>
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

  // Parse milestones for journey display
  const journeyMilestones = [
    {
      label: 'Checked in at New York (JFK)',
      details: '14:05 local · Confirmed',
      status: 'confirmed' as const,
    },
    {
      label: 'Loaded on EK 0201',
      details: '15:20 local · Confirmed',
      status: 'confirmed' as const,
    },
    {
      label: 'Arrived at Dubai',
      details: '19:58 GST · Confirmed',
      status: 'confirmed' as const,
    },
    {
      label: 'Transferred to your next flight, EK 0507',
      details: 'Estimated · Expected before 20:40 GST',
      status: 'estimated' as const,
    },
    {
      label: 'Arrives with you at destination',
      details: 'Not yet expected · will be confirmed after loading',
      status: 'upcoming' as const,
    },
  ];

  const isEstimated = status.estimated_notice !== null;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-gray-900 px-4 py-3 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-red-600">
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
                <rect x="4" y="7" width="16" height="13" rx="2" />
                <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M4 13h16" />
              </svg>
            </span>
            <span className="text-lg font-bold">Baggage360</span>
          </div>
          <span className="rounded border border-orange-500 border-dashed bg-orange-100 px-2 py-0.5 text-xs font-bold tracking-wide text-orange-700">
            SIMULATED
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-md p-4">
        <div className="mb-4 flex items-center justify-between text-sm">
          <span className="text-gray-600">Your bag</span>
          <strong className="text-base">Bag {status.bag_tag}</strong>
        </div>

        <div className="space-y-4">
          {/* Status Headline */}
          <StatusHeadline
            isEstimated={isEstimated}
            statusLabel={status.status_label}
            message={
              status.estimated_notice ||
              'Your bag is being processed normally'
            }
          />

          {/* Last Confirmed */}
          <section
            className="rounded-lg border border-gray-300 bg-white p-4 shadow-sm"
            aria-labelledby="last-confirmed"
          >
            <span className="mb-1 block text-xs font-bold uppercase tracking-wide text-gray-500">
              Last confirmed
            </span>
            <h2 id="last-confirmed" className="mb-1 flex items-center gap-2 text-lg font-bold">
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
              {status.latest_confirmed_milestone}
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

          {/* Estimated Next Step */}
          {status.estimated_notice && (
            <section
              className="rounded-lg border-2 border-dashed border-orange-500 bg-orange-50 p-4"
              aria-labelledby="estimated-next"
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
              <h2 id="estimated-next" className="mb-1 text-lg font-bold">
                What we expect next
              </h2>
              <p className="text-sm">{status.estimated_notice}</p>
              <p className="mt-2 text-xs text-gray-600">
                Why it is uncertain: your inbound flight was late, so we are working to
                move your bag onto your next flight. We will confirm once it has been
                scanned.
              </p>
            </section>
          )}

          {/* Bag Journey */}
          <BagJourney milestones={journeyMilestones} />

          {/* Next Expected Update */}
          {status.next_expected_update && (
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
                  Next expected update {status.next_expected_update}
                </strong>
                <span className="text-xs text-gray-600">
                  Last updated{' '}
                  {new Date(status.last_updated_at).toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit',
                    timeZone: 'Asia/Dubai',
                    timeZoneName: 'short',
                  })}
                </span>
              </div>
            </div>
          )}

          {/* Link to Delayed Case */}
          {status.delayed_case_reference && (
            <Link
              to={`/passenger/cases/${status.delayed_case_reference}`}
              className="flex items-center gap-2 px-1 py-2 font-bold text-blue-600 hover:underline"
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
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
              View your delayed-bag case {status.delayed_case_reference}
            </Link>
          )}
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
        Data source: GET /api/v1/passenger/bags/{bagTag}/status
      </footer>
    </div>
  );
}
