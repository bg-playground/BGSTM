import { useEffect, useState } from "react";
import traceabilityApi, { type Metrics } from "../api/traceability";
import { useToast } from "../components/Toast";
import { LoadingSpinner } from "../components/LoadingSpinner";

export default function MetricsDashboardPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const { showToast } = useToast();

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const data = await traceabilityApi.getMetrics();
      setMetrics(data);
    } catch (error) {
      console.error("Failed to load metrics:", error);
      showToast("Failed to load metrics", "error");
    } finally {
      setLoading(false);
    }
  };

  const getAlgorithmColor = (algorithm: string) => {
    switch (algorithm) {
      case "hybrid":
        return "bg-purple-100 text-purple-700";
      case "keyword_match":
        return "bg-blue-100 text-blue-700";
      case "semantic_similarity":
        return "bg-green-100 text-green-700";
      case "heuristic":
        return "bg-orange-100 text-orange-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No metrics available</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Metrics Dashboard</h1>
        <button
          onClick={loadMetrics}
          disabled={loading}
          className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:bg-gray-400"
        >
          Refresh
        </button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Requirements Coverage</h3>
          <div className="flex items-end gap-2">
            <p className="text-4xl font-bold text-blue-600">{metrics.coverage_percentage.toFixed(1)}%</p>
            <p className="text-sm text-gray-500 mb-1">
              ({metrics.total_requirements} total)
            </p>
          </div>
          <div className="mt-3 w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all"
              style={{ width: `${metrics.coverage_percentage}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Suggestion Acceptance Rate</h3>
          <div className="flex items-end gap-2">
            <p className="text-4xl font-bold text-green-600">{metrics.suggestion_acceptance_rate.toFixed(1)}%</p>
            <p className="text-sm text-gray-500 mb-1">
              ({metrics.total_suggestions} total)
            </p>
          </div>
          <div className="mt-3 w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-green-600 h-3 rounded-full transition-all"
              style={{ width: `${metrics.suggestion_acceptance_rate}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600 mb-2">Total Links</h3>
          <p className="text-4xl font-bold text-purple-600">{metrics.total_links}</p>
          <div className="mt-3 text-sm text-gray-600">
            <div className="flex justify-between">
              <span>Manual:</span>
              <span className="font-semibold">{metrics.manual_links}</span>
            </div>
            <div className="flex justify-between">
              <span>AI-Suggested:</span>
              <span className="font-semibold">{metrics.ai_suggested_links}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Counts Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow text-center">
          <p className="text-2xl font-bold text-gray-800">{metrics.total_requirements}</p>
          <p className="text-sm text-gray-600">Requirements</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow text-center">
          <p className="text-2xl font-bold text-gray-800">{metrics.total_test_cases}</p>
          <p className="text-sm text-gray-600">Test Cases</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow text-center">
          <p className="text-2xl font-bold text-gray-800">{metrics.total_suggestions}</p>
          <p className="text-sm text-gray-600">Suggestions</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow text-center">
          <p className="text-2xl font-bold text-gray-800">{metrics.total_links}</p>
          <p className="text-sm text-gray-600">Links</p>
        </div>
      </div>

      {/* Suggestion Status Breakdown */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Suggestion Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-green-50 rounded">
            <p className="text-3xl font-bold text-green-600">{metrics.accepted_suggestions}</p>
            <p className="text-sm text-gray-600">Accepted</p>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded">
            <p className="text-3xl font-bold text-yellow-600">{metrics.pending_suggestions}</p>
            <p className="text-sm text-gray-600">Pending</p>
          </div>
          <div className="text-center p-4 bg-red-50 rounded">
            <p className="text-3xl font-bold text-red-600">{metrics.rejected_suggestions}</p>
            <p className="text-sm text-gray-600">Rejected</p>
          </div>
        </div>
      </div>

      {/* Algorithm Breakdown */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">Algorithm Performance</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Algorithm
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Accepted
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rejected
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pending
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acceptance Rate
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {metrics.algorithm_breakdown.map((algo) => (
                <tr key={algo.algorithm} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 text-sm font-medium rounded ${getAlgorithmColor(algo.algorithm)}`}>
                      {algo.algorithm.replace(/_/g, " ").toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center text-sm text-gray-900">{algo.total_suggestions}</td>
                  <td className="px-6 py-4 text-center text-sm text-green-600 font-semibold">
                    {algo.accepted_suggestions}
                  </td>
                  <td className="px-6 py-4 text-center text-sm text-red-600 font-semibold">
                    {algo.rejected_suggestions}
                  </td>
                  <td className="px-6 py-4 text-center text-sm text-yellow-600 font-semibold">
                    {algo.pending_suggestions}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <span className="text-sm font-semibold text-gray-900">{algo.acceptance_rate.toFixed(1)}%</span>
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{ width: `${algo.acceptance_rate}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
