import { useEffect, useState } from "react";
import traceabilityApi, { type TraceabilityMatrix } from "../api/traceability";
import { useToast } from "../components/Toast";
import { LoadingSpinner } from "../components/LoadingSpinner";

export default function TraceabilityMatrixPage() {
  const [matrix, setMatrix] = useState<TraceabilityMatrix | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const { showToast } = useToast();

  useEffect(() => {
    loadMatrix();
  }, []);

  const loadMatrix = async () => {
    try {
      setLoading(true);
      const data = await traceabilityApi.getMatrix();
      setMatrix(data);
    } catch (error) {
      console.error("Failed to load traceability matrix:", error);
      showToast("Failed to load traceability matrix", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: "csv" | "json") => {
    try {
      setExporting(true);
      const blob = await traceabilityApi.exportMatrix(format);
      const filename = `traceability_matrix_${new Date().toISOString().split("T")[0]}.${format}`;
      traceabilityApi.downloadExport(blob, filename);
      showToast(`Exported traceability matrix as ${format.toUpperCase()}`, "success");
    } catch (error) {
      console.error(`Failed to export as ${format}:`, error);
      showToast(`Failed to export as ${format.toUpperCase()}`, "error");
    } finally {
      setExporting(false);
    }
  };

  const getCoverageColor = (status: string) => {
    switch (status) {
      case "covered":
        return "text-green-700 bg-green-100";
      case "partially_covered":
        return "text-yellow-700 bg-yellow-100";
      case "uncovered":
        return "text-red-700 bg-red-100";
      default:
        return "text-gray-700 bg-gray-100";
    }
  };

  const getLinkStatusBadge = (status: string) => {
    switch (status) {
      case "accepted":
        return <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-700">Accepted</span>;
      case "pending":
        return <span className="px-2 py-1 text-xs rounded bg-yellow-100 text-yellow-700">Pending</span>;
      case "rejected":
        return <span className="px-2 py-1 text-xs rounded bg-red-100 text-red-700">Rejected</span>;
      default:
        return <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-700">{status}</span>;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (!matrix) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Traceability Matrix</h1>
        <div className="flex gap-2">
          <button
            onClick={() => handleExport("csv")}
            disabled={exporting}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            Export CSV
          </button>
          <button
            onClick={() => handleExport("json")}
            disabled={exporting}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            Export JSON
          </button>
          <button
            onClick={loadMatrix}
            disabled={loading}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 disabled:bg-gray-400"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Coverage Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Coverage Percentage</h3>
          <p className="text-3xl font-bold text-blue-600">{matrix.coverage_percentage.toFixed(1)}%</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Covered Requirements</h3>
          <p className="text-3xl font-bold text-green-600">
            {matrix.covered_requirements} / {matrix.total_requirements}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Uncovered Requirements</h3>
          <p className="text-3xl font-bold text-red-600">{matrix.uncovered_requirements}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Orphan Test Cases</h3>
          <p className="text-3xl font-bold text-yellow-600">{matrix.orphan_test_cases}</p>
        </div>
      </div>

      {/* Requirements Matrix */}
      <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">Requirements Coverage</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Requirement
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Coverage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Linked Test Cases
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {matrix.matrix.map((req) => (
                <tr key={req.requirement_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{req.requirement_title}</div>
                    {req.external_id && <div className="text-sm text-gray-500">{req.external_id}</div>}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 text-xs font-medium rounded-full ${getCoverageColor(req.coverage_status)}`}>
                      {req.coverage_status.replace("_", " ").toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {req.linked_test_cases.length === 0 ? (
                      <span className="text-sm text-gray-500 italic">No linked test cases</span>
                    ) : (
                      <div className="space-y-2">
                        {req.linked_test_cases.map((tc) => (
                          <div key={tc.test_case_id} className="flex items-center gap-2">
                            <span className="text-sm text-gray-900">{tc.title}</span>
                            {getLinkStatusBadge(tc.link_status)}
                            {tc.confidence_score && (
                              <span className="text-xs text-gray-500">({(tc.confidence_score * 100).toFixed(0)}%)</span>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Orphan Test Cases */}
      {matrix.orphans.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-800">Orphan Test Cases</h2>
            <p className="text-sm text-gray-600 mt-1">Test cases with no linked requirements</p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Test Case
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    External ID
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {matrix.orphans.map((orphan) => (
                  <tr key={orphan.test_case_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900">{orphan.title}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{orphan.external_id || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
