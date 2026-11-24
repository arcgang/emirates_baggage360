/**
 * BagJourney - Bag journey milestone list with confirmed/estimated/upcoming markers
 */
import React from 'react';
import MilestoneList from './MilestoneList';

interface BagJourneyProps {
  milestones: Array<{
    label: string;
    details: string;
    status: 'confirmed' | 'estimated' | 'upcoming';
  }>;
}

export default function BagJourney({ milestones }: BagJourneyProps) {
  return (
    <section
      className="rounded-lg border border-gray-300 bg-white p-4 shadow-sm"
      aria-labelledby="bag-journey-heading"
    >
      <h2 id="bag-journey-heading" className="mb-3 text-lg font-bold">
        Bag journey
      </h2>
      <MilestoneList milestones={milestones} />
    </section>
  );
}
