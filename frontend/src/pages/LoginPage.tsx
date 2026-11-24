import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth-context';

interface RoleCard {
  id: string;
  label: string;
  capabilities: string;
  route: string;
  icon: string;
}

const roles: RoleCard[] = [
  {
    id: 'operations',
    label: 'Operations Lead',
    capabilities: 'Sees: at-risk bag groups, case timelines, recommendations. Can approve or reject. Cannot see: partner-only task entry or executive aggregates.',
    route: '/operations/cockpit',
    icon: 'grid',
  },
  {
    id: 'partner',
    label: 'Partner Handler',
    capabilities: 'Sees: only tasks assigned to your role and station, with masked passenger data. Can acknowledge and add evidence. Cannot see: risk scores or other cases.',
    route: '/partner/tasks',
    icon: 'list',
  },
  {
    id: 'passenger',
    label: 'Passenger',
    capabilities: 'Sees: your own bag status, split into confirmed and estimated. Cannot see: internal operations signals, other passengers\' bags.',
    route: '/passenger/bags',
    icon: 'user',
  },
  {
    id: 'executive',
    label: 'Executive',
    capabilities: 'Sees: aggregate reliability, recovery and passenger-impact trends. Cannot see: bag-level or task-level detail.',
    route: '/executive/overview',
    icon: 'chart',
  },
];

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [purpose, setPurpose] = useState('Operational recovery');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [rateLimited, setRateLimited] = useState(false);

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    setRateLimited(false);

    // Validation
    if (!email.trim()) {
      setError('Enter your work email or staff ID.');
      setIsLoading(false);
      return;
    }

    if (!password.trim()) {
      setError('Enter your password.');
      setIsLoading(false);
      return;
    }

    try {
      await login({ email, password });
      setIsAuthenticated(true);
    } catch (err) {
      if (err instanceof Error) {
        if (err.message.includes('429') || err.message.includes('Too many')) {
          setRateLimited(true);
          setError('Too many attempts. Try again in 5 minutes.');
        } else {
          setError('We could not sign you in with those details. Check them and try again.');
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRoleSelect = (role: RoleCard) => {
    setSelectedRole(role.id);
    // Redirect to role home
    setTimeout(() => {
      navigate(role.route);
    }, 300);
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex" style={{ background: '#F7F6F4' }}>
        {/* Brand Panel */}
        <div className="w-1/2 bg-[#231F20] text-white p-16 flex flex-col justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#E7002A] rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 stroke-white fill-none" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="4" y="7" width="16" height="13" rx="2"/>
                <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M4 13h16"/>
              </svg>
            </div>
            <span className="text-2xl font-bold">Baggage360</span>
          </div>

          <div>
            <h1 className="text-5xl font-bold leading-tight mb-6">One trusted view of every bag's journey</h1>
            <div className="w-16 h-1 bg-[#E7002A] my-6"></div>
            <p className="text-lg leading-relaxed" style={{ color: '#E4E0DC', maxWidth: '520px' }}>
              Find at-risk bags before the connection is lost. Approve the recovery action, dispatch it to the right handler, and keep the passenger honestly informed.
            </p>
          </div>

          <div className="flex gap-3 items-start p-4 border border-[#5A5552] rounded-lg" style={{ color: '#E4E0DC', maxWidth: '520px' }}>
            <svg className="w-5 h-5 stroke-[#FFC46B] fill-none flex-shrink-0 mt-0.5" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9"/>
              <path d="M12 11v6M12 7.5v.5"/>
            </svg>
            <div className="text-sm">
              <strong>SIMULATED demo environment.</strong> All flights, bag tags, passengers and handlers are synthetic. No live Emirates systems are connected and no real passenger data is shown.
            </div>
          </div>
        </div>

        {/* Form Panel */}
        <div className="w-1/2 p-16 flex flex-col gap-6">
          <form onSubmit={handleLogin} className="bg-white border border-[#D9D5D1] rounded-xl shadow-lg p-8 max-w-[560px]">
            <h2 className="text-2xl font-bold mb-1">Sign in</h2>
            <p className="text-[#68645F] mb-6">Access is limited to your role and your stated purpose.</p>

            {error && (
              <div className={`flex gap-2 items-start p-3 rounded-lg border mb-4 ${
                rateLimited ? 'bg-[#FFF1DE] text-[#A65A00] border-[#E8C48F]' : 'bg-[#FDE9E7] text-[#B42318] border-[#E9B4AE]'
              }`} role="alert">
                <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 3 2 20h20L12 3z"/>
                  <path d="M12 10v5M12 18v.5"/>
                </svg>
                <span className="text-sm">{error}</span>
              </div>
            )}

            <div className="mb-4">
              <label htmlFor="email" className="block font-semibold text-sm mb-2">Work email or staff ID</label>
              <input
                id="email"
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-11 px-3 border border-[#8A857F] rounded-lg"
                disabled={isLoading}
                placeholder="mariam.alsuwaidi@baggage360.demo"
              />
            </div>

            <div className="mb-4">
              <label htmlFor="password" className="block font-semibold text-sm mb-2">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full h-11 px-3 border border-[#8A857F] rounded-lg"
                disabled={isLoading}
                placeholder="Demo1234!"
              />
            </div>

            <div className="mb-4">
              <label htmlFor="purpose" className="block font-semibold text-sm mb-2">Purpose of access</label>
              <select
                id="purpose"
                value={purpose}
                onChange={(e) => setPurpose(e.target.value)}
                className="w-full h-11 px-3 border border-[#8A857F] rounded-lg"
                disabled={isLoading}
              >
                <option>Operational recovery</option>
                <option>Task execution</option>
                <option>Passenger enquiry</option>
                <option>Performance review</option>
              </select>
              <p className="text-xs text-[#68645F] mt-1">Recorded in the audit trail.</p>
            </div>

            <button
              type="submit"
              disabled={isLoading || rateLimited}
              className="w-full h-11 bg-[#E7002A] text-white font-semibold rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="5" y="11" width="14" height="9" rx="2"/>
                <path d="M8 11V8a4 4 0 0 1 8 0v3"/>
              </svg>
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>

            <p className="text-xs text-[#68645F] mt-3">
              Sessions end after a period of inactivity. Repeated failed attempts are rate-limited.
            </p>
          </form>
        </div>
      </div>
    );
  }

  // Role selection screen
  return (
    <div className="min-h-screen flex" style={{ background: '#F7F6F4' }}>
      {/* Brand Panel - same as login */}
      <div className="w-1/2 bg-[#231F20] text-white p-16 flex flex-col justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#E7002A] rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 stroke-white fill-none" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="4" y="7" width="16" height="13" rx="2"/>
              <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M4 13h16"/>
            </svg>
          </div>
          <span className="text-2xl font-bold">Baggage360</span>
        </div>

        <div>
          <h1 className="text-5xl font-bold leading-tight mb-6">One trusted view of every bag's journey</h1>
          <div className="w-16 h-1 bg-[#E7002A] my-6"></div>
          <p className="text-lg leading-relaxed" style={{ color: '#E4E0DC', maxWidth: '520px' }}>
            Find at-risk bags before the connection is lost. Approve the recovery action, dispatch it to the right handler, and keep the passenger honestly informed.
          </p>
        </div>

        <div className="flex gap-3 items-start p-4 border border-[#5A5552] rounded-lg" style={{ color: '#E4E0DC', maxWidth: '520px' }}>
          <svg className="w-5 h-5 stroke-[#FFC46B] fill-none flex-shrink-0 mt-0.5" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="9"/>
            <path d="M12 11v6M12 7.5v.5"/>
          </svg>
          <div className="text-sm">
            <strong>SIMULATED demo environment.</strong> All flights, bag tags, passengers and handlers are synthetic. No live Emirates systems are connected and no real passenger data is shown.
          </div>
        </div>
      </div>

      {/* Role Selection Panel */}
      <div className="w-1/2 p-16 flex flex-col gap-6">
        <div className="max-w-[560px]">
          <h3 className="text-lg font-semibold mb-1">
            Demo role entry{' '}
            <span className="inline-flex items-center gap-1 px-2 py-0.5 border border-dashed border-[#A65A00] rounded bg-[#FFF1DE] text-[#A65A00] text-xs font-bold tracking-wider">SIMULATED SSO</span>
          </h3>
          <p className="text-[#68645F] mb-4">Choose a role to open its home screen. Each role sees only its own destinations.</p>

          <div className="grid grid-cols-2 gap-3">
            {roles.map((role) => (
              <button
                key={role.id}
                onClick={() => handleRoleSelect(role)}
                className={`p-4 border rounded-xl text-left hover:shadow-lg transition-all ${
                  selectedRole === role.id
                    ? 'border-2 border-[#231F20] bg-white shadow-lg'
                    : 'border-[#D9D5D1] bg-white'
                }`}
              >
                <div className="flex items-center gap-2 font-bold text-[15px] mb-2">
                  <span>{role.label}</span>
                  {selectedRole === role.id && (
                    <span className="ml-auto px-2 py-0.5 bg-[#EEECE9] text-[#231F20] text-xs rounded-full border border-[#D9D5D1]">Selected</span>
                  )}
                </div>
                <p className="text-xs text-[#68645F] mb-2 leading-relaxed">{role.capabilities}</p>
                <div className="flex items-center gap-1.5 text-xs font-semibold text-[#1769AA]">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M13 6l6 6-6 6"/>
                  </svg>
                  {role.route}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
