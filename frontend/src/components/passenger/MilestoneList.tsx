/**
 * MilestoneList - Timeline list with colored dots for confirmed/estimated/upcoming milestones
 */
import React from 'react';

interface Milestone {
  label: string;
  details: string;
  status: 'confirmed' | 'estimated' | 'upcoming';
}

interface MilestoneListProps {
  milestones: Milestone[];
}

export default function MilestoneList({ milestones }: MilestoneListProps) {
  return (
    <ol className="flex flex-col gap-0" aria-label="Bag journey milestones">
      {milestones.map((milestone, index) => (
        <li
          key={index}
          className={`relative flex gap-3 pb-4 ${
            index === milestones.length - 1 ? 'border-transparent' : ''
          } ${
            milestone.status === 'confirmed'
              ? 'border-l-2 border-green-600 ml-2'
              : milestone.status === 'estimated'
              ? 'border-l-2 border-dashed border-gray-400 ml-2'
              : 'border-l-2 border-dashed border-gray-300 ml-2'
          }`}
          style={
            index === milestones.length - 1
              ? { borderLeftColor: 'transparent' }
              : {}
          }
        >
          <span
            className={`absolute left-[-9px] top-0.5 flex h-4 w-4 items-center justify-center rounded-full border-2 ${
              milestone.status === 'confirmed'
                ? 'border-green-600 bg-green-600'
                : milestone.status === 'estimated'
                ? 'border-orange-500 border-dashed bg-white'
                : 'border-gray-400 border-dashed bg-white'
            }`}
            aria-hidden="true"
          />
          <div className="pl-4">
            <div className="font-bold">{milestone.label}</div>
            <div className="text-sm text-gray-600">{milestone.details}</div>
          </div>
        </li>
      ))}
    </ol>
  );
}
