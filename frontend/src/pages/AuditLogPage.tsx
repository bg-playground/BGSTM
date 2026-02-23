import React, { useCallback, useEffect, useState } from 'react';
import { auditLogApi } from '../api/auditLog';
import type { AuditLogEntry } from '../api/auditLog';
import { usersApi } from '../api/users';
import type { UserResponse } from '../api/users';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Pagination } from '../components/Pagination';
import { useToast } from '../context/ToastContext';

const PAGE_SIZE = 50;

const formatDate = (iso: string) =>
  new Date(iso).toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

const AuditLogPage: React.FC = () => {
  const { showToast } = useToast();

  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // Filter state
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [filterUserId, setFilterUserId] = useState('');
  const [filterAction, setFilterAction] = useState('');
  const [filterResourceType, setFilterResourceType] = useState('');
  const [filterDateFrom, setFilterDateFrom] = useState('');
  const [filterDateTo, setFilterDateTo] = useState('');

  // Expanded rows
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const loadEntries = useCallback(
    async (targetPage: number) => {
      try {
        setLoading(true);
        setError(false);
        const data = await auditLogApi.list({
          user_id: filterUserId || undefined,
          action: filterAction || undefined,
          resource_type: filterResourceType || undefined,
          date_from: filterDateFrom || undefined,
          date_to: filterDateTo || undefined,
          skip: (targetPage - 1) * PAGE_SIZE,
          limit: PAGE_SIZE,
        });
        setEntries(data.entries);
        setTotal(data.total);
      } catch {
        setError(true);
        showToast('Failed to load audit log', 'error');
      } finally {
        setLoading(false);
      }
    },
    [filterUserId, filterAction, filterResourceType, filterDateFrom, filterDateTo, showToast],
  );

  // Load users for filter dropdown (best-effort)
  useEffect(() => {
    usersApi.list(0, 500).then((data) => setUsers(data.users)).catch((err) => {
      console.error('Failed to load users for filter:', err);
    });
  }, []);

  useEffect(() => {
    loadEntries(page);
  }, [page, loadEntries]);

  const handleApplyFilters = () => {
    setPage(1);
    loadEntries(1);
  };

  const handleClearFilters = () => {
    setFilterUserId('');
    setFilterAction('');
    setFilterResourceType('');
    setFilterDateFrom('');
    setFilterDateTo('');
    setPage(1);
  };

  const toggleRow = (id: string) => {
    setExpandedRows((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const getUserLabel = (userId: string) => {
    const u = users.find((u) => u.id === userId);
    return u ? (u.full_name ?? u.email) : userId;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Audit Log</h1>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Filters</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">User</label>
            <select
              value={filterUserId}
              onChange={(e) => setFilterUserId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Action</label>
            <input
              type="text"
              placeholder="e.g. requirement.created"
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Entity Type</label>
            <input
              type="text"
              placeholder="e.g. requirement"
              value={filterResourceType}
              onChange={(e) => setFilterResourceType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">From Date</label>
            <input
              type="datetime-local"
              value={filterDateFrom}
              onChange={(e) => setFilterDateFrom(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">To Date</label>
            <input
              type="datetime-local"
              value={filterDateTo}
              onChange={(e) => setFilterDateTo(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
        <div className="flex gap-3 mt-4">
          <button
            onClick={handleApplyFilters}
            className="px-5 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Apply Filters
          </button>
          <button
            onClick={handleClearFilters}
            className="px-5 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div className="flex items-center justify-center h-48">
          <LoadingSpinner size="lg" />
        </div>
      ) : error ? (
        <div className="bg-red-50 rounded-lg p-8 text-center">
          <p className="text-red-700 font-medium mb-3">Failed to load audit log entries.</p>
          <button
            onClick={() => loadEntries(page)}
            className="px-5 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      ) : entries.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <p className="text-gray-600 text-lg">No audit log entries match your filters.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  User
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Action
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Entity Type
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Entity ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Details
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {entries.map((entry) => {
                const isExpanded = expandedRows.has(entry.id);
                const detailsJson = entry.details ? JSON.stringify(entry.details) : null;
                const isLong = detailsJson && detailsJson.length > 80;
                return (
                  <tr key={entry.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">
                      {formatDate(entry.created_at)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700 max-w-[160px] truncate">
                      {getUserLabel(entry.user_id)}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                        {entry.action}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{entry.resource_type}</td>
                    <td className="px-4 py-3 text-sm text-gray-500 font-mono text-xs max-w-[120px] truncate">
                      {entry.resource_id}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 max-w-xs">
                      {detailsJson ? (
                        <>
                          <span className={isExpanded ? '' : 'line-clamp-1'}>
                            {isExpanded ? detailsJson : detailsJson.slice(0, 80)}
                          </span>
                          {isLong && (
                            <button
                              onClick={() => toggleRow(entry.id)}
                              className="text-primary-600 hover:underline text-xs ml-1"
                            >
                              {isExpanded ? 'Show less' : '...more'}
                            </button>
                          )}
                        </>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} pages={pages} total={total} onPageChange={setPage} />
    </div>
  );
};

export default AuditLogPage;
