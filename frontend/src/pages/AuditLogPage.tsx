import React, { useCallback, useEffect, useState } from 'react';
import { auditLogApi } from '../api/auditLog';
import type { AuditLogEntry } from '../api/auditLog';
import { usersApi } from '../api/users';
import type { ManagedUser } from '../api/users';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Pagination } from '../components/Pagination';
import { useToast } from '../context/ToastContext';

const PAGE_SIZES = [25, 50, 100];

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, '0');
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  );
}

function exportCsv(entries: AuditLogEntry[], userMap: Record<string, string>) {
  const header = ['Timestamp', 'User', 'Action', 'Resource Type', 'Resource ID', 'Details'];
  const rows = entries.map((e) => [
    formatDateTime(e.created_at),
    userMap[e.user_id] ?? e.user_id,
    e.action,
    e.resource_type,
    e.resource_id,
    e.details ? JSON.stringify(e.details) : '',
  ]);
  const csv = [header, ...rows]
    .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    .join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'audit-log.csv';
  a.click();
  URL.revokeObjectURL(url);
}

export const AuditLogPage: React.FC = () => {
  const { showToast } = useToast();

  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [loading, setLoading] = useState(true);

  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [userMap, setUserMap] = useState<Record<string, string>>({});

  // Filters
  const [filterUserId, setFilterUserId] = useState('');
  const [filterAction, setFilterAction] = useState('');
  const [filterDateFrom, setFilterDateFrom] = useState('');
  const [filterDateTo, setFilterDateTo] = useState('');

  // Expandable details
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const pages = Math.max(1, Math.ceil(total / pageSize));

  const loadUsers = useCallback(async () => {
    try {
      const res = await usersApi.list(0, 500);
      setUsers(res.data.users);
      const map: Record<string, string> = {};
      for (const u of res.data.users) {
        map[u.id] = u.full_name ?? u.email;
      }
      setUserMap(map);
    } catch {
      // non-fatal
    }
  }, []);

  const loadEntries = useCallback(
    async (targetPage: number) => {
      try {
        setLoading(true);
        const skip = (targetPage - 1) * pageSize;
        const res = await auditLogApi.list({
          skip,
          limit: pageSize,
          user_id: filterUserId || undefined,
          action: filterAction || undefined,
          date_from: filterDateFrom || undefined,
          date_to: filterDateTo || undefined,
        });
        setEntries(res.data.entries);
        setTotal(res.data.total);
      } catch {
        showToast('Failed to load audit log', 'error');
      } finally {
        setLoading(false);
      }
    },
    [pageSize, filterUserId, filterAction, filterDateFrom, filterDateTo, showToast],
  );

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  useEffect(() => {
    loadEntries(page);
  }, [page, loadEntries]);

  const handleApplyFilters = useCallback(() => {
    setPage(1);
    loadEntries(1);
  }, [loadEntries]);

  const handleClearFilters = useCallback(() => {
    setFilterUserId('');
    setFilterAction('');
    setFilterDateFrom('');
    setFilterDateTo('');
    setPage(1);
  }, []);

  // Re-fetch when filters are cleared
  useEffect(() => {
    if (!filterUserId && !filterAction && !filterDateFrom && !filterDateTo) {
      loadEntries(1);
    }
  }, [filterUserId, filterAction, filterDateFrom, filterDateTo, loadEntries]);

  const toggleExpand = useCallback((id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const KNOWN_ACTIONS = [
    'user_login',
    'user_registered',
    'requirement_created',
    'requirement_updated',
    'requirement_deleted',
    'test_case_created',
    'test_case_updated',
    'test_case_deleted',
    'suggestion_accepted',
    'suggestion_rejected',
    'link_created',
    'link_deleted',
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Audit Log</h1>
        <button
          onClick={() => exportCsv(entries, userMap)}
          disabled={entries.length === 0}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-40 disabled:cursor-not-allowed text-sm"
        >
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">User</label>
            <select
              value={filterUserId}
              onChange={(e) => setFilterUserId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-primary-500 focus:border-primary-500"
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
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All actions</option>
              {KNOWN_ACTIONS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">From date</label>
            <input
              type="datetime-local"
              value={filterDateFrom}
              onChange={(e) => setFilterDateFrom(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">To date</label>
            <input
              type="datetime-local"
              value={filterDateTo}
              onChange={(e) => setFilterDateTo(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
        <div className="flex gap-3 mt-4">
          <button
            onClick={handleApplyFilters}
            className="px-4 py-2 bg-primary-600 text-white rounded-md text-sm hover:bg-primary-700"
          >
            Apply Filters
          </button>
          <button
            onClick={handleClearFilters}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md text-sm hover:bg-gray-300"
          >
            Clear Filters
          </button>
          <div className="ml-auto flex items-center gap-2">
            <label className="text-xs text-gray-600">Rows per page:</label>
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setPage(1);
              }}
              className="px-2 py-1 border border-gray-300 rounded-md text-sm"
            >
              {PAGE_SIZES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <LoadingSpinner size="lg" />
        </div>
      ) : entries.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-10 text-center">
          <p className="text-gray-500">No audit log entries found.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Timestamp', 'User', 'Action', 'Resource Type', 'Resource ID', 'Details'].map(
                  (col) => (
                    <th
                      key={col}
                      className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap"
                    >
                      {col}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {entries.map((entry) => (
                <tr key={entry.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
                    {formatDateTime(entry.created_at)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
                    {userMap[entry.user_id] ?? entry.user_id}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-800 whitespace-nowrap">
                    {entry.action}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
                    {entry.resource_type}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
                    {entry.resource_id}
                  </td>
                  <td className="px-4 py-3 text-sm max-w-xs">
                    {entry.details ? (
                      <button
                        onClick={() => toggleExpand(entry.id)}
                        className="text-primary-600 hover:underline text-xs"
                      >
                        {expandedIds.has(entry.id) ? '▲ collapse' : '▶ expand'}
                      </button>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                    {expandedIds.has(entry.id) && entry.details && (
                      <pre className="mt-1 text-xs bg-gray-100 rounded p-2 overflow-x-auto max-w-xs">
                        {JSON.stringify(entry.details, null, 2)}
                      </pre>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} pages={pages} total={total} onPageChange={setPage} />
    </div>
  );
};
