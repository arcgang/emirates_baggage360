/**
 * StatusHeadline - Headline card with estimated/confirmed chip and plain-language status message
 */
import React from 'react';

interface StatusHeadlineProps {
  isEstimated: boolean;
  statusLabel: string;
  message: string;
}

export default function StatusHeadline({
  isEstimated,
  statusLabel,
  message,
}: StatusHeadlineProps) {
  return (
    <section
      className={`rounded-lg border-l-6 p-5 ${
        isEstimated
          ? 'border-orange-600 bg-orange-50'
          : 'border-green-600 bg-green-50'
      }`}
      aria-labelledby="status-headline"
    >
      <div className="mb-2">
        <span
          className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${
            isEstimated
              ? 'border-orange-500 border-dashed bg-orange-100 text-orange-700'
              : 'border-green-600 bg-green-100 text-green-700'
          }`}
        >
          {isEstimated ? (
            <>
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
                <path d="M12 7v5l3 2" />
              </svg>
              Estimated, not confirmed
            </>
          ) : (
            <>
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
            </>
          )}
        </span>
      </div>
      <h1 id="status-headline" className="mb-1 text-2xl font-bold leading-tight">
        {statusLabel}
      </h1>
      <p className="text-sm text-gray-600">{message}</p>
    </section>
  );
}
