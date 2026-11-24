/**
 * Sidebar navigation component.
 * Shows role-specific navigation links.
 */
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../lib/auth-context';
import { cn } from '../../lib/utils';

interface NavItem {
  path: string;
  label: string;
  roles: string[];
}

const navItems: NavItem[] = [
  { path: '/operations/cockpit', label: 'Operations Cockpit', roles: ['operations'] },
  { path: '/partner/tasks', label: 'Task Queue', roles: ['partner'] },
  { path: '/passenger/bags', label: 'My Bags', roles: ['passenger'] },
  { path: '/executive/overview', label: 'Executive Overview', roles: ['executive'] },
];

export function Sidebar() {
  const { user } = useAuth();
  const location = useLocation();

  const visibleItems = navItems.filter((item) =>
    user?.role ? item.roles.includes(user.role) : false
  );

  return (
    <aside className="app-sidebar bg-ek-black text-white flex flex-col">
      <div className="p-6">
        <div className="text-ek-red text-2xl font-bold">Baggage360</div>
        <div className="text-ek-gold text-sm mt-1">Emirates</div>
      </div>

      <nav className="flex-1 px-3">
        {visibleItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              'block px-4 py-3 rounded-md mb-1 transition-colors',
              location.pathname.startsWith(item.path)
                ? 'bg-ek-red text-white'
                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
            )}
          >
            {item.label}
          </Link>
        ))}
      </nav>

      {user && (
        <div className="p-4 border-t border-gray-700">
          <div className="text-sm text-gray-400">{user.role}</div>
          <div className="text-sm font-medium truncate">{user.display_name}</div>
        </div>
      )}
    </aside>
  );
}
