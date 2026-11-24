/**
 * Top navigation bar with user actions.
 */
import { useAuth } from '../../lib/auth-context';

export function TopNav() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout on error
      window.location.href = '/login';
    }
  };

  return (
    <div className="flex items-center justify-between px-6 py-4">
      <div>
        {/* Breadcrumbs or page title can go here */}
      </div>

      <div className="flex items-center gap-4">
        {user && (
          <>
            <div className="text-sm">
              <div className="font-medium">{user.display_name}</div>
              <div className="text-gray-500">{user.role}</div>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm font-medium text-white bg-ek-red rounded-md hover:bg-red-700 transition-colors"
            >
              Logout
            </button>
          </>
        )}
      </div>
    </div>
  );
}
