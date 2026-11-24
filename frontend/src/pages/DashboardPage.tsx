/**
 * Default dashboard page after login.
 * Provides role-based navigation to main application sections.
 */
import { Link } from 'react-router-dom';
import { useAuth } from '../lib/auth-context';

export function DashboardPage() {
  const { user } = useAuth();

  // Role-based navigation cards
  const getNavigationCards = () => {
    const role = user?.role || '';
    
    const cards: Array<{ title: string; description: string; link: string; linkText: string }> = [];
    
    if (role === 'operations') {
      cards.push({
        title: 'Operations Cockpit',
        description: 'Monitor exception cases, review recommendations, and approve recovery actions.',
        link: '/operations/cockpit',
        linkText: 'Go to Cockpit'
      });
    }
    
    if (role === 'partner') {
      cards.push({
        title: 'Task Queue',
        description: 'View assigned tasks, acknowledge work, and submit evidence.',
        link: '/partner/tasks',
        linkText: 'Go to Tasks'
      });
    }
    
    if (role === 'passenger') {
      cards.push({
        title: 'Baggage Status',
        description: 'Check the status of your bags and delayed-bag cases.',
        link: '/passenger/bags/example/status',
        linkText: 'Check Bag Status'
      });
    }
    
    if (role === 'executive') {
      cards.push({
        title: 'Executive Overview',
        description: 'View aggregated reliability metrics, exception trends, and passenger impact indicators.',
        link: '/executive/overview',
        linkText: 'Go to Overview'
      });
    }
    
    return cards;
  };

  const navigationCards = getNavigationCards();

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-4">
        Welcome, {user?.display_name}
      </h1>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <p className="text-gray-600">
          You are logged in as <span className="font-medium">{user?.role}</span>.
        </p>
        <p className="text-gray-600 mt-2">
          Use the navigation below to access your role-specific features.
        </p>
      </div>

      {navigationCards.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {navigationCards.map((card, index) => (
            <div key={index} className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <h2 className="text-lg font-semibold mb-2">{card.title}</h2>
              <p className="text-sm text-gray-600 mb-4">{card.description}</p>
              <Link
                to={card.link}
                className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700"
              >
                {card.linkText}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                  <path d="M5 12h14M13 6l6 6-6 6"/>
                </svg>
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
