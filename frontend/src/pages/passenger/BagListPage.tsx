/**
 * Passenger Bag List Page
 * Shows all bags for the authenticated passenger
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';
import { useAuth } from '../../lib/auth-context';

interface BagItem {
  bag_tag: string;
  flight_number: string;
  status: string;
  last_location?: string;
}

export default function BagListPage() {
  const { user } = useAuth();
  const [bags, setBags] = useState<BagItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBags = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/v1/passenger/bags', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch bags');
        }

        const data = await response.json();
        setBags(data.bags || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load bags');
      } finally {
        setLoading(false);
      }
    };

    fetchBags();
  }, []);

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">My Bags</h1>

        {loading && (
          <div className="text-center py-8">Loading your bags...</div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {!loading && !error && bags.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No bags found. Enter a bag tag to check its status.
          </div>
        )}

        {!loading && bags.length > 0 && (
          <div className="space-y-4">
            {bags.map((bag) => (
              <Link
                key={bag.bag_tag}
                to={`/passenger/bags/${bag.bag_tag}/status`}
                className="block bg-white border border-gray-200 rounded-lg p-4 hover:border-ek-red hover:shadow-md transition-all"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-semibold text-lg">{bag.bag_tag}</div>
                    <div className="text-sm text-gray-600 mt-1">
                      Flight: {bag.flight_number}
                    </div>
                    {bag.last_location && (
                      <div className="text-sm text-gray-500 mt-1">
                        Last seen: {bag.last_location}
                      </div>
                    )}
                  </div>
                  <div className="text-right">
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                        bag.status === 'delivered'
                          ? 'bg-green-100 text-green-800'
                          : bag.status === 'in_transit'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {bag.status.replace(/_/g, ' ')}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h2 className="font-semibold mb-2">Search by Bag Tag</h2>
          <p className="text-sm text-gray-600 mb-4">
            Enter your bag tag number to check its status
          </p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              const bagTag = formData.get('bagTag') as string;
              if (bagTag) {
                window.location.href = `/passenger/bags/${bagTag}/status`;
              }
            }}
            className="flex gap-2"
          >
            <input
              type="text"
              name="bagTag"
              placeholder="e.g., EK001234567"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-ek-red text-white rounded-md hover:bg-red-700"
            >
              Check Status
            </button>
          </form>
        </div>
      </div>
    </Layout>
  );
}
