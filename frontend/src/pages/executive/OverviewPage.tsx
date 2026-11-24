/**
 * Executive Overview Page
 * Displays executive reliability and impact overview with KPIs, trend chart, and category breakdown
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiClient, ApiError } from '../../lib/api-client';
import { useAuth } from '../../lib/auth-context';
import { ExecutiveOverviewResponse } from '../../types/executive';
import { KPICards } from '../../components/executive/KPICards';
import { TrendChart } from '../../components/executive/TrendChart';
import { CategoryBreakdown } from '../../components/executive/CategoryBreakdown';

export const OverviewPage: React.FC = () => {
  const { user } = useAuth();
  const [overview, setOverview] = useState<ExecutiveOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Date range: Last 14 days (matching seed data 2026-11-10 to 2026-11-23)
  const [fromDate, setFromDate] = useState('2026-11-10');
  const [toDate, setToDate] = useState('2026-11-23');
  
  const fetchOverview = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiClient.get<ExecutiveOverviewResponse>(
        `/executive/overview?from_date=${fromDate}&to_date=${toDate}`
      );
      setOverview(data);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 403) {
          setError('Your role cannot open this view. Executive overview is available to the Executive role only.');
        } else if (err.status === 400) {
          setError('The start date must be on or before the end date. Choose a valid range.');
        } else {
          setError(err.detail || 'Failed to load executive overview');
        }
      } else {
        setError('Network error. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchOverview();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fromDate, toDate]);
  
  const getFreshnessWarning = () => {
    if (!overview) return null;
    
    if (overview.freshness_status === 'mixed' || overview.freshness_status === 'stale') {
      return (
        <div className="inline-flex items-center gap-2 px-2 py-0.5 rounded-full bg-orange-50 border border-orange-200 text-orange-700 text-xs font-semibold ml-1.5">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9"/>
            <path d="M12 7v5l3 2"/>
          </svg>
          <span>Sources fresh 2 of 3</span>
        </div>
      );
    }
    
    return null;
  };
  
  // Format last refresh time
  const formatRefreshTime = () => {
    if (!overview) return '';
    const d = new Date(overview.generated_at);
    return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) + ' GST';
  };

  return (
    <div className="min-h-screen" style={{ background: '#F7F6F4' }}>
      {/* Top Navigation */}
      <header className="flex items-center gap-6 px-8 min-h-16 bg-[#231F20] text-white">
        <div className="flex items-center gap-2.5 text-white font-bold text-lg">
          <div className="w-8 h-8 bg-[#E7002A] rounded-lg flex items-center justify-center">
            <svg className="w-4 h-4 stroke-white fill-none" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="4" y="7" width="16" height="13" rx="2"/>
              <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M4 13h16"/>
            </svg>
          </div>
          Baggage360
        </div>

        <nav aria-label="Executive">
          <Link
            to="/executive/overview"
            className="inline-flex items-center min-h-16 px-2 text-white font-semibold border-b-4 border-b-[#E7002A]"
            aria-current="page"
          >
            Overview
          </Link>
        </nav>

        <div className="ml-auto flex items-center gap-4 text-sm">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 border border-dashed border-[#A65A00] rounded bg-[#FFF1DE] text-[#A65A00] text-xs font-bold tracking-wider">
            SIMULATED DATA
          </span>
          <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-[#3A3536] text-white text-xs font-semibold border border-[#5A5552]">
            Executive Operations Sponsor
          </span>
          <Link to="/login" className="text-white font-semibold underline">
            Sign out
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-8">
        {loading ? (
          <div>
            <div className="mb-6">
              <div className="h-8 w-80 bg-gray-100 rounded mb-2 animate-pulse"></div>
              <div className="h-4 w-96 bg-gray-100 rounded animate-pulse"></div>
            </div>
            <div className="grid grid-cols-6 gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="bg-white border border-gray-200 rounded-xl shadow-sm p-4">
                  <div className="h-3 w-20 bg-gray-100 rounded mb-2 animate-pulse"></div>
                  <div className="h-8 w-24 bg-gray-100 rounded mb-2 animate-pulse"></div>
                  <div className="h-4 w-32 bg-gray-100 rounded animate-pulse"></div>
                </div>
              ))}
            </div>
            <p className="text-sm text-gray-600 mt-4">Loading overview for {fromDate} to {toDate}…</p>
          </div>
        ) : error ? (
          <div>
            <h1 className="text-2xl font-bold mb-4">Baggage operations overview</h1>
            <div className="flex gap-2 items-start p-3 rounded-lg border border-red-200 bg-red-50 text-sm text-red-800" role="alert">
              <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                {error.includes('403') || error.includes('role') ? (
                  <>
                    <rect x="5" y="11" width="14" height="9" rx="2"/>
                    <path d="M8 11V8a4 4 0 0 1 8 0v3"/>
                  </>
                ) : (
                  <>
                    <path d="M12 3 2 20h20L12 3z"/>
                    <path d="M12 10v5M12 18v.5"/>
                  </>
                )}
              </svg>
              <span>{error}</span>
            </div>
          </div>
        ) : !overview || !overview.kpis || overview.kpis.length === 0 ? (
          <div>
            <h1 className="text-2xl font-bold mb-4">Baggage operations overview</h1>
            <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
              <strong className="block mb-2">No data for range</strong>
              <p className="text-sm text-gray-600">
                No exceptions recorded for this range. Choose a wider date range, or check back after the next data refresh.
              </p>
            </div>
          </div>
        ) : (
          <>
            {/* Page title and date range controls */}
            <div className="flex items-end justify-between gap-4 mb-6">
              <div>
                <h1 className="text-3xl font-bold mb-1">Baggage operations overview</h1>
                <p className="text-sm text-gray-600">
                  Aggregate view for all DXB transfer banks · Last refresh {formatRefreshTime()}
                  {getFreshnessWarning()}
                </p>
              </div>
              
              <div className="flex items-center gap-3" role="group" aria-label="Date range">
                <div className="inline-flex items-center gap-2 min-h-[44px] px-3 border border-gray-400 rounded-lg bg-white font-semibold">
                  <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                    <rect x="3" y="5" width="18" height="16" rx="2"/>
                    <path d="M3 10h18M8 3v4M16 3v4"/>
                  </svg>
                  <div>
                    <span className="text-xs font-bold tracking-wider uppercase text-gray-600 block leading-tight">From</span>
                    <input 
                      type="date" 
                      value={fromDate} 
                      onChange={(e) => setFromDate(e.target.value)}
                      className="border-none p-0 text-sm font-semibold bg-transparent focus:outline-none focus:ring-0"
                    />
                  </div>
                </div>
                
                <div className="inline-flex items-center gap-2 min-h-[44px] px-3 border border-gray-400 rounded-lg bg-white font-semibold">
                  <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                    <rect x="3" y="5" width="18" height="16" rx="2"/>
                    <path d="M3 10h18M8 3v4M16 3v4"/>
                  </svg>
                  <div>
                    <span className="text-xs font-bold tracking-wider uppercase text-gray-600 block leading-tight">To</span>
                    <input 
                      type="date" 
                      value={toDate} 
                      onChange={(e) => setToDate(e.target.value)}
                      className="border-none p-0 text-sm font-semibold bg-transparent focus:outline-none focus:ring-0"
                    />
                  </div>
                </div>
                
                <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-gray-100 border border-gray-300 text-xs font-semibold text-gray-800">
                  Last 14 days
                </span>
              </div>
            </div>
            
            {/* KPI Cards */}
            <KPICards kpis={overview.kpis} />
            
            {/* Trend Chart and Category Breakdown */}
            <div className="grid grid-cols-[1.7fr_1fr] gap-5 mt-6">
              <section className="bg-white border border-gray-200 rounded-xl shadow-sm p-5" aria-labelledby="trend-heading">
                <h2 id="trend-heading" className="text-base font-semibold mb-1">
                  Exceptions and recoveries per day
                </h2>
                <p className="text-sm text-gray-600 mb-2">
                  {fromDate.replace(/-/g, '/')} to {toDate.replace(/-/g, '/')} · SIMULATED
                </p>
                <TrendChart trendData={overview.trend_data} />
              </section>
              
              <section className="bg-white border border-gray-200 rounded-xl shadow-sm p-5" aria-labelledby="category-heading">
                <CategoryBreakdown totalBags={205} />
              </section>
            </div>
            
            {/* Provenance and freshness */}
            <section 
              className="bg-white border border-gray-200 rounded-xl shadow-sm p-5 mt-6 grid grid-cols-3 gap-5 text-sm"
              aria-label="Provenance and freshness"
            >
              <div>
                <h3 className="text-xs font-semibold tracking-wider uppercase text-gray-600 mb-1">Sources</h3>
                <p>Wasla (fresh 6 min) · BHS/BRS (fresh 4 min) · Flight operations (fresh 2 min) · Handler feed (stale 14 min)</p>
              </div>
              <div>
                <h3 className="text-xs font-semibold tracking-wider uppercase text-gray-600 mb-1">Last refresh</h3>
                <p>23 Nov 2026, 20:10 GST (16:10Z). Metrics are recalculated from stored events for the selected range.</p>
              </div>
              <div>
                <h3 className="text-xs font-semibold tracking-wider uppercase text-gray-600 mb-1">Interpretation limits</h3>
                <p>Demo dataset, simulated. Not a financial outcome and not a statement about real Emirates performance.</p>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
};
