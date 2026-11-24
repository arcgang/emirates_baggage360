/**
 * Category Breakdown component for executive overview
 * Displays exception categories with horizontal bars and counts
 */

interface CategoryData {
  name: string;
  count: number;
  percentage: number;
}

interface CategoryBreakdownProps {
  totalBags: number;
}

export const CategoryBreakdown: React.FC<CategoryBreakdownProps> = ({ totalBags }) => {
  // Hardcoded category data matching wireframe (205 total bags)
  const categories: CategoryData[] = [
    { name: 'Connection risk', count: 92, percentage: 45 },
    { name: 'Missing scan', count: 63, percentage: 31 },
    { name: 'Misroute', count: 31, percentage: 15 },
    { name: 'Customs hold', count: 19, percentage: 9 },
  ];
  
  return (
    <div>
      <h2 className="text-base font-semibold mb-1">
        Passenger impact by exception category
      </h2>
      <p className="text-sm text-gray-600 mb-3">
        Bags affected, aggregate only · {totalBags} in total
      </p>
      
      <div className="flex flex-col gap-3.5">
        {categories.map((category) => (
          <div 
            key={category.name}
            className="grid grid-cols-[150px_1fr_64px] gap-3 items-center"
          >
            <span className="text-sm">{category.name}</span>
            <div 
              className="h-3.5 bg-gray-100 rounded-full overflow-hidden"
              role="img"
              aria-label={`${category.name} ${category.count} bags, ${category.percentage} percent`}
            >
              <div 
                className="h-full bg-black"
                style={{ width: `${category.percentage}%` }}
              />
            </div>
            <strong className="text-sm text-right">
              {category.count} · {category.percentage}%
            </strong>
          </div>
        ))}
      </div>
      
      <div className="mt-5 flex gap-2 items-start p-2.5 rounded-lg border border-blue-200 bg-blue-50 text-sm text-blue-800">
        <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="9"/>
          <path d="M12 11v6M12 7.5v.5"/>
        </svg>
        <span>
          Category counts are for the whole network window. They do not rank stations or people, 
          and they do not show individual bags or cases.
        </span>
      </div>
    </div>
  );
};
