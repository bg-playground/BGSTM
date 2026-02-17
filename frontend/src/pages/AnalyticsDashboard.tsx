import React, { useEffect, useState } from 'react';
import { analyticsApi, type AlgorithmComparison, type AcceptanceRates, type ReviewVelocity } from '../api/analytics';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useToast } from '../components/Toast';

// Recommendation thresholds
const EXCELLENT_THRESHOLD = 0.8;
const GOOD_THRESHOLD = 0.6;
const FAIR_THRESHOLD = 0.4;
const HIGH_BACKLOG_THRESHOLD = 50;

export const AnalyticsDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);
  const [algorithmComparison, setAlgorithmComparison] = useState<AlgorithmComparison[]>([]);
  const [acceptanceRates, setAcceptanceRates] = useState<AcceptanceRates | null>(null);
  const [reviewVelocity, setReviewVelocity] = useState<ReviewVelocity | null>(null);
  const { showToast } = useToast();

  const loadData = React.useCallback(async () => {
    try {
      setLoading(true);
      const [comparison, rates, velocity] = await Promise.all([
        analyticsApi.getAlgorithmComparison(),
        analyticsApi.getAcceptanceRates(timeRange),
        analyticsApi.getReviewVelocity(timeRange),
      ]);

      setAlgorithmComparison(comparison);
      setAcceptanceRates(rates);
      setReviewVelocity(velocity);
    } catch (error) {
      console.error('Error loading analytics:', error);
      showToast('Failed to load analytics', 'error');
    } finally {
      setLoading(false);
    }
  }, [timeRange, showToast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const getBestAlgorithm = () => {
    if (algorithmComparison.length === 0) return null;
    return algorithmComparison[0]; // Already sorted by acceptance rate
  };

  const bestAlgo = getBestAlgorithm();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Suggestion Analytics</h1>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(Number(e.target.value))}
          className="border rounded px-4 py-2"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500 mb-2">Overall Acceptance Rate</div>
          <div className="text-3xl font-bold text-green-600">
            {acceptanceRates ? (acceptanceRates.overall.rate * 100).toFixed(1) : 0}%
          </div>
          <div className="text-xs text-gray-500 mt-2">
            {acceptanceRates?.overall.accepted} accepted of {acceptanceRates?.overall.total} total
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500 mb-2">Best Algorithm</div>
          <div className="text-3xl font-bold text-blue-600">
            {bestAlgo?.algorithm.toUpperCase() || 'N/A'}
          </div>
          <div className="text-xs text-gray-500 mt-2">
            {bestAlgo ? `${(bestAlgo.acceptance_rate * 100).toFixed(1)}% acceptance` : 'No data'}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500 mb-2">Avg Review Time</div>
          <div className="text-3xl font-bold text-purple-600">
            {reviewVelocity?.avg_time_to_review_hours.toFixed(1) || 0}h
          </div>
          <div className="text-xs text-gray-500 mt-2">
            {reviewVelocity?.daily_review_rate.toFixed(1) || 0} reviews/day
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-500 mb-2">Pending Backlog</div>
          <div className="text-3xl font-bold text-orange-600">
            {reviewVelocity?.pending_backlog || 0}
          </div>
          <div className="text-xs text-gray-500 mt-2">
            Awaiting review
          </div>
        </div>
      </div>

      {/* Algorithm Comparison Table */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="px-6 py-4 border-b">
          <h2 className="text-xl font-bold text-gray-900">Algorithm Performance Comparison</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Algorithm</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Accepted</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rejected</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acceptance Rate</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Confidence</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recommendation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {algorithmComparison.map((algo, index) => (
                <tr key={algo.algorithm} className={index === 0 ? 'bg-green-50' : ''}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-semibold text-gray-900">{algo.algorithm.toUpperCase()}</span>
                    {index === 0 && (
                      <span className="ml-2 px-2 py-1 text-xs font-medium bg-green-200 text-green-800 rounded">
                        Best
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-700">{algo.total_suggestions}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-green-600 font-medium">{algo.accepted}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-red-600 font-medium">{algo.rejected}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${algo.acceptance_rate * 100}%` }}
                        />
                      </div>
                      <span className="font-semibold">{(algo.acceptance_rate * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                    {(algo.avg_confidence * 100).toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {algo.acceptance_rate > EXCELLENT_THRESHOLD ? '✅ Excellent - Use for critical items' :
                     algo.acceptance_rate > GOOD_THRESHOLD ? '✔️ Good - General use' :
                     algo.acceptance_rate > FAIR_THRESHOLD ? '⚠️ Fair - Needs tuning' :
                     '❌ Poor - Avoid or increase threshold'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recommendations Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-bold text-blue-900 mb-4">💡 Recommendations</h3>
        <ul className="space-y-2">
          {bestAlgo && bestAlgo.acceptance_rate > EXCELLENT_THRESHOLD && (
            <li className="text-blue-900">
              • <strong>{bestAlgo.algorithm.toUpperCase()}</strong> has excellent accuracy ({(bestAlgo.acceptance_rate * 100).toFixed(1)}%).
              Consider using it as your default algorithm.
            </li>
          )}
          {reviewVelocity && reviewVelocity.pending_backlog > HIGH_BACKLOG_THRESHOLD && (
            <li className="text-blue-900">
              • You have {reviewVelocity.pending_backlog} pending suggestions. Consider enabling notifications or
              scheduling regular review sessions.
            </li>
          )}
          {acceptanceRates && acceptanceRates.overall.rate < 0.5 && (
            <li className="text-blue-900">
              • Overall acceptance rate is below 50%. Consider increasing confidence thresholds to reduce noise.
            </li>
          )}
          {algorithmComparison.find(a => a.algorithm === 'llm_embedding') && (
            <li className="text-blue-900">
              • LLM algorithm is available. Compare its accuracy vs cost to determine if it's worth using for your use case.
            </li>
          )}
        </ul>
      </div>
    </div>
  );
};
