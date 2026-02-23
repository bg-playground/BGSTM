import React, { useCallback, useEffect, useState } from 'react';
import { auditLogApi } from '../api/auditLog';
import type { AuditLogEntry } from '../api/auditLog';
import { usersApi } from '../api/users';
import type { UserRecord } from '../api/users';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Pagination } from '../components/Pagination';
import { useToast } from '../context/ToastContext';

const PAGE_SIZE = 25;

function formatRelativeTime(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);
  if (diffSec < 60) return `${diffSec}s ago`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDays = Math.floor(diffHr / 24);
  return `${diffDays}d ago`;
}

function formatFullDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString();
}

function formatResource(entry: AuditLogEntry): string {
  const type = entry.resource_type
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
  return `${type} #${entry.resource_id}`;
}

const DetailsCell: React.FC<{ details: Record<string, unknown> | null }> = ({ details }) => {
  const [expanded, setExpanded] = useState(false);
  if (!details || Object.keys(details).length === 0) return <span className="text-gray-400">—</span>;
  return (
    <div>
      <button
        onClick={() => setExpanded((v) => !v)}
        className="text-xs text-blue-600 hover:underline focus:outline-none"
      >
        {expanded ? 'Collapse ▲' : 'Expand ▼'}
      </button>
      {expanded && (
        <pre className="mt-1 text-xs bg-gray-100 rounded p-2 overflow-x-auto max-w-xs">
          {JSON.stringify(details, null, 2)}
        </pre>
      )}
    </div>
  );
};

export const AuditLogPage: React.FC = () => {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [users, setUsers] = useState<UserRecord[]>([]);
  // Accumulate all known action types across pages for the filter dropdown
  const [allActions, setAllActions] = useState<string[]>([]);

  // Filters
  const [filterUserId, setFilterUserId] = useState('');
  const [filterAction, setFilterAction] = useState('');
  const [filterDateFrom, setFilterDateFrom] = useState('');
  const [filterDateTo, setFilterDateTo] = useState('');
  const [filterSearch, setFilterSearch] = useState('');

  const { showToast } = useToast();

  const pages = Math.ceil(total / PAGE_SIZE);

  const loadEntries = useCallback(
    async (targetPage: number) => {
      try {
        setLoading(true);
        setError(null);
        const skip = (targetPage - 1) * PAGE_SIZE;
        const data = await auditLogApi.list({
          user_id: filterUserId || undefined,
          action: filterAction || undefined,
          date_from: filterDateFrom || undefined,
          date_to: filterDateTo || undefined,
          skip,
          limit: PAGE_SIZE,
        });
        setEntries(data.entries);
        setTotal(data.total);
        // Accumulate action types seen across pages so the dropdown is comprehensive
        setAllActions((prev) => {
          const merged = new Set([...prev, ...data.entries.map((e) => e.action)]);
          return Array.from(merged).sort();
        });
      } catch {
        setError('Failed to load audit log');
        showToast('Failed to load audit log', 'error');
      } finally {
        setLoading(false);
      }
    },
    [filterUserId, filterAction, filterDateFrom, filterDateTo, showToast],
  );

  const loadUsers = useCallback(async () => {
    try {
      const data = await usersApi.list();
      setUsers(data.users);
    } catch {
      // non-critical
    }
  }, []);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  useEffect(() => {
    setPage(1);
    loadEntries(1);
  }, [filterUserId, filterAction, filterDateFrom, filterDateTo, loadEntries]);

  const handlePageChange = useCallback(
    (p: number) => {
      setPage(p);
      loadEntries(p);
    },
    [loadEntries],
  );

  const handleClearFilters = useCallback(() => {
    setFilterUserId('');
    setFilterAction('');
    setFilterDateFrom('');
    setFilterDateTo('');
    setFilterSearch('');
  }, []);

  // Text search is applied client-side to the currently loaded page (backend has no full-text search param)
  const displayedEntries = filterSearch
    ? entries.filter(
        (e) =>
          e.action.toLowerCase().includes(filterSearch.toLowerCase()) ||
          JSON.stringify(e.details ?? {})
            .toLowerCase()
            .includes(filterSearch.toLowerCase()),
      )
    : entries;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Audit Log</h1>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">User</label>
            <select
              value={filterUserId}
              onChange={(e) => setFilterUserId(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All users</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.full_name ?? u.email}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Action</label>
            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All actions</option>
              {allActions.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">From</label>
            <input
              type="datetime-local"
              value={filterDateFrom}
              onChange={(e) => setFilterDateFrom(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">To</label>
            <input
              type="datetime-local"
              value={filterDateTo}
              onChange={(e) => setFilterDateTo(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
        <div className="mt-3 flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            placeholder="Search action or details…"
            value={filterSearch}
            onChange={(e) => setFilterSearch(e.target.value)}
            className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            onClick={handleClearFilters}
            className="px-4 py-2 text-sm rounded border border-gray-300 hover:bg-gray-50"
          >
            Clear filters
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex justify-center items-center h-48">
            <LoadingSpinner />
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-500 mb-4">{error}</p>
            <button
              onClick={() => loadEntries(page)}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        ) : displayedEntries.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No audit entries found</p>
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
                    Resource
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Details
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {displayedEntries.map((entry) => {
                  const userRecord = users.find((u) => u.id === entry.user_id);
                  return (
                    <tr key={entry.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span
                          title={formatFullDate(entry.created_at)}
                          className="text-sm text-gray-900 cursor-default"
                        >
                          {formatRelativeTime(entry.created_at)}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                        {userRecord ? (userRecord.full_name ?? userRecord.email) : entry.user_id}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className="text-sm font-mono text-gray-800">{entry.action}</span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                        {formatResource(entry)}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <DetailsCell details={entry.details} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        {!loading && !error && displayedEntries.length > 0 && (
          <div className="px-4 py-3 border-t border-gray-200">
            <Pagination page={page} pages={pages} total={total} onPageChange={handlePageChange} />
          </div>
        )}
      </div>
    </div>
  );
};
