import React, { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { adminApi } from '../api/adminApi';
import type { AuditLogEntry, AdminUser } from '../api/adminApi';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Pagination } from '../components/Pagination';
import { useToast } from '../context/ToastContext';

const PAGE_SIZES = [10, 25, 50, 100];

export const AuditLogPage: React.FC = () => {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const { showToast } = useToast();

  const page = parseInt(searchParams.get('page') ?? '1', 10);
  const pageSize = parseInt(searchParams.get('per_page') ?? '25', 10);
  const userId = searchParams.get('user_id') ?? '';
  const action = searchParams.get('action') ?? '';
  const resourceType = searchParams.get('resource_type') ?? '';
  const dateFrom = searchParams.get('date_from') ?? '';
  const dateTo = searchParams.get('date_to') ?? '';

  const pages = Math.ceil(total / pageSize);

  const setParam = useCallback(
    (key: string, value: string) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        if (value) {
          next.set(key, value);
        } else {
          next.delete(key);
        }
        next.set('page', '1');
        return next;
      });
    },
    [setSearchParams],
  );

  const handlePageChange = useCallback(
    (newPage: number) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        next.set('page', String(newPage));
        return next;
      });
    },
    [setSearchParams],
  );

  const loadEntries = useCallback(async () => {
    try {
      setLoading(true);
      const skip = (page - 1) * pageSize;
      const res = await adminApi.getAuditLogs({
        skip,
        limit: pageSize,
        ...(userId && { user_id: userId }),
        ...(action && { action }),
        ...(resourceType && { resource_type: resourceType }),
        ...(dateFrom && { date_from: dateFrom }),
        ...(dateTo && { date_to: dateTo }),
      });
      setEntries(res.data.entries);
      setTotal(res.data.total);
    } catch {
      showToast('Failed to load audit log', 'error');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, userId, action, resourceType, dateFrom, dateTo, showToast]);

  useEffect(() => {
    loadEntries();
  }, [loadEntries]);

  useEffect(() => {
    adminApi.getUsers(0, 500).then((res) => setUsers(res.data.users)).catch(() => {});
  }, []);

  const getUserLabel = (uid: string) => {
    const u = users.find((x) => x.id === uid);
    return u ? (u.full_name ?? u.email) : uid;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Audit Log</h1>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">From</label>
          <input
            type="datetime-local"
            value={dateFrom}
            onChange={(e) => setParam('date_from', e.target.value)}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">To</label>
          <input
            type="datetime-local"
            value={dateTo}
            onChange={(e) => setParam('date_to', e.target.value)}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">User</label>
          <select
            value={userId}
            onChange={(e) => setParam('user_id', e.target.value)}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
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
          <input
            type="text"
            value={action}
            onChange={(e) => setParam('action', e.target.value)}
            placeholder="e.g. requirement.created"
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Resource Type</label>
          <input
            type="text"
            value={resourceType}
            onChange={(e) => setParam('resource_type', e.target.value)}
            placeholder="e.g. requirement"
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Page Size</label>
          <select
            value={pageSize}
            onChange={(e) => setParam('per_page', e.target.value)}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
          >
            {PAGE_SIZES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <LoadingSpinner size="lg" />
        </div>
      ) : entries.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-500">No audit log entries found.</div>
      ) : (
        <div className="overflow-x-auto bg-white rounded-lg shadow">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                {['Timestamp', 'User', 'Action', 'Resource Type', 'Resource ID', 'Details'].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {entries.map((entry) => (
                <React.Fragment key={entry.id}>
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-3 whitespace-nowrap text-gray-700">
                      {new Date(entry.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-gray-700">{getUserLabel(entry.user_id)}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                        {entry.action}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-700">{entry.resource_type}</td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-600">{entry.resource_id}</td>
                    <td className="px-4 py-3">
                      {entry.details && (
                        <button
                          onClick={() => setExpandedRow(expandedRow === entry.id ? null : entry.id)}
                          className="text-primary-600 hover:text-primary-800 text-xs underline"
                        >
                          {expandedRow === entry.id ? 'Hide' : 'Show'}
                        </button>
                      )}
                    </td>
                  </tr>
                  {expandedRow === entry.id && entry.details && (
                    <tr>
                      <td colSpan={6} className="px-4 py-3 bg-gray-50">
                        <pre className="text-xs text-gray-700 whitespace-pre-wrap overflow-x-auto max-h-48">
                          {JSON.stringify(entry.details, null, 2)}
                        </pre>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} pages={pages} total={total} onPageChange={handlePageChange} />
    </div>
  );
};
