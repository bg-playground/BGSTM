import React, { useCallback, useEffect, useState } from 'react';
import { adminApi } from '../api/admin';
import type { AuditLogEntry, AuditLogParams } from '../api/admin';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Pagination } from '../components/Pagination';
import { useToast } from '../context/ToastContext';

const PAGE_SIZE = 25;

const ACTION_OPTIONS = [
  'created_requirement',
  'updated_requirement',
  'deleted_requirement',
  'created_test_case',
  'updated_test_case',
  'deleted_test_case',
  'accepted_suggestion',
  'rejected_suggestion',
  'login',
  'logout',
  'role_changed',
  'user_deactivated',
];

const ENTITY_TYPE_OPTIONS = ['requirement', 'test_case', 'suggestion', 'user', 'link'];

function formatTimestamp(ts: string): string {
  try {
    return new Date(ts).toLocaleString();
  } catch {
    return ts;
  }
}

function formatDetails(details: Record<string, unknown> | null): string {
  if (!details) return '—';
  try {
    return JSON.stringify(details, null, 2);
  } catch {
    return String(details);
  }
}

export const AuditLogPage: React.FC = () => {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(0);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [userFilter, setUserFilter] = useState('');
  const [entityTypeFilter, setEntityTypeFilter] = useState('');

  const { showToast } = useToast();

  const loadEntries = useCallback(
    async (targetPage: number) => {
      try {
        setLoading(true);
        const params: AuditLogParams = { page: targetPage, page_size: PAGE_SIZE };
        if (fromDate) params.from_date = fromDate;
        if (toDate) params.to_date = toDate;
        if (actionFilter) params.action = actionFilter;
        if (userFilter) params.user_email = userFilter;
        if (entityTypeFilter) params.entity_type = entityTypeFilter;
        const data = await adminApi.getAuditLog(params);
        setEntries(data.items);
        setTotal(data.total);
        setPages(data.pages);
      } catch (err: unknown) {
        const status = (err as { response?: { status?: number } })?.response?.status;
        if (status === 401 || status === 403) {
          showToast('Access denied. Admin role required.', 'error');
        } else {
          showToast('Failed to load audit log', 'error');
        }
      } finally {
        setLoading(false);
      }
    },
    [fromDate, toDate, actionFilter, userFilter, entityTypeFilter, showToast],
  );

  useEffect(() => {
    loadEntries(page);
  }, [page, loadEntries]);

  const handleFilter = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      setPage(1);
      loadEntries(1);
    },
    [loadEntries],
  );

  const handleResetFilters = useCallback(() => {
    setFromDate('');
    setToDate('');
    setActionFilter('');
    setUserFilter('');
    setEntityTypeFilter('');
    setPage(1);
  }, []);

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Audit Log</h1>

      {/* Filters */}
      <form onSubmit={handleFilter} className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">From Date</label>
            <input
              type="datetime-local"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">To Date</label>
            <input
              type="datetime-local"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Action</label>
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Actions</option>
              {ACTION_OPTIONS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">User (email)</label>
            <input
              type="text"
              value={userFilter}
              onChange={(e) => setUserFilter(e.target.value)}
              placeholder="Filter by email..."
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Entity Type</label>
            <select
              value={entityTypeFilter}
              onChange={(e) => setEntityTypeFilter(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Types</option>
              {ENTITY_TYPE_OPTIONS.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end gap-2">
            <button
              type="submit"
              className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700"
            >
              Apply Filters
            </button>
            <button
              type="button"
              onClick={handleResetFilters}
              className="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-50"
            >
              Reset
            </button>
          </div>
        </div>
      </form>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-16">
            <LoadingSpinner size="lg" />
          </div>
        ) : entries.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <p className="text-lg font-medium">No audit log entries found</p>
            <p className="text-sm mt-1">Try adjusting your filters</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Entity Type
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Details
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {entries.map((entry) => (
                  <tr key={entry.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
                      {formatTimestamp(entry.timestamp)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-800 whitespace-nowrap">
                      {entry.user_email ?? '—'}
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900 whitespace-nowrap">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                        {entry.action}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
                      {entry.entity_type ?? '—'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {entry.details ? (
                        <button
                          onClick={() => setExpandedId(expandedId === entry.id ? null : entry.id)}
                          className="text-primary-600 hover:text-primary-800 text-xs underline"
                        >
                          {expandedId === entry.id ? 'Hide' : 'Show'}
                        </button>
                      ) : (
                        '—'
                      )}
                      {expandedId === entry.id && entry.details && (
                        <pre className="mt-2 text-xs bg-gray-50 border border-gray-200 rounded p-2 max-w-xs overflow-auto whitespace-pre-wrap">
                          {formatDetails(entry.details)}
                        </pre>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {!loading && entries.length > 0 && (
          <div className="px-4 py-3 border-t border-gray-200">
            <Pagination page={page} pages={pages} total={total} onPageChange={handlePageChange} />
          </div>
        )}
      </div>
    </div>
  );
};
