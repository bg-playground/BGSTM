import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { adminApi } from '../api/admin';
import type { AuditLogEntry } from '../api/admin';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useToast } from '../context/ToastContext';

const PAGE_SIZE = 50;

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString();
}

function formatDetails(details: Record<string, unknown> | null): string {
  if (!details) return '—';
  try {
    return JSON.stringify(details);
  } catch {
    return '—';
  }
}

export const AuditLogPage: React.FC = () => {
  const { showToast } = useToast();

  const [allEntries, setAllEntries] = useState<AuditLogEntry[]>([]);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  // Filters
  const [actionFilter, setActionFilter] = useState('');
  const [resourceTypeFilter, setResourceTypeFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [search, setSearch] = useState('');

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await adminApi.fetchAuditLog({
        action: actionFilter || undefined,
        resourceType: resourceTypeFilter || undefined,
        dateFrom: dateFrom || undefined,
        dateTo: dateTo || undefined,
        skip: 0,
        limit: 500,
      });
      setAllEntries(data.entries);
    } catch {
      showToast('Failed to load audit log', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [actionFilter, resourceTypeFilter, dateFrom, dateTo, showToast]);

  useEffect(() => {
    load();
  }, [load]);

  const filteredEntries = useMemo(() => {
    if (!search.trim()) return allEntries;
    const q = search.trim().toLowerCase();
    return allEntries.filter(
      (e) => e.action.toLowerCase().includes(q) || formatDetails(e.details).toLowerCase().includes(q)
    );
  }, [allEntries, search]);

  const totalPages = Math.max(1, Math.ceil(filteredEntries.length / PAGE_SIZE));
  const paginatedEntries = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return filteredEntries.slice(start, start + PAGE_SIZE);
  }, [filteredEntries, page]);

  const handleApplyFilters = useCallback(() => {
    setPage(1);
    load();
  }, [load]);

  const handleExportCsv = useCallback(() => {
    try {
      const rows = [
        ['Timestamp', 'User ID', 'Action', 'Resource Type', 'Resource ID', 'Details'],
        ...filteredEntries.map((e) => [
          e.created_at,
          e.user_id ?? '',
          e.action,
          e.resource_type ?? '',
          e.resource_id ?? '',
          formatDetails(e.details),
        ]),
      ];
      const csv = rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'audit-log.csv';
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      showToast('Failed to export audit log', 'error');
    }
  }, [filteredEntries, showToast]);

  return (
    <main className="container mx-auto px-4 py-8" aria-label="Audit Log">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Audit Log</h1>
        <button
          onClick={handleExportCsv}
          className="px-4 py-2 bg-primary-700 text-white rounded-md text-sm font-medium hover:bg-primary-800 transition-colors"
          aria-label="Export audit log to CSV"
        >
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label htmlFor="audit-action" className="block text-xs font-medium text-gray-700 mb-1">
              Action
            </label>
            <input
              id="audit-action"
              type="text"
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              placeholder="e.g. requirement.created"
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label htmlFor="audit-resource-type" className="block text-xs font-medium text-gray-700 mb-1">
              Resource Type
            </label>
            <input
              id="audit-resource-type"
              type="text"
              value={resourceTypeFilter}
              onChange={(e) => setResourceTypeFilter(e.target.value)}
              placeholder="e.g. requirement"
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label htmlFor="audit-date-from" className="block text-xs font-medium text-gray-700 mb-1">
              Date From
            </label>
            <input
              id="audit-date-from"
              type="datetime-local"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label htmlFor="audit-date-to" className="block text-xs font-medium text-gray-700 mb-1">
              Date To
            </label>
            <input
              id="audit-date-to"
              type="datetime-local"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
        <div className="flex items-end gap-3 mt-4">
          <div className="flex-1">
            <label htmlFor="audit-search" className="block text-xs font-medium text-gray-700 mb-1">
              Search (action / details)
            </label>
            <input
              id="audit-search"
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleApplyFilters()}
              placeholder="Keyword search…"
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button
            onClick={handleApplyFilters}
            className="px-4 py-2 bg-primary-700 text-white rounded-md text-sm font-medium hover:bg-primary-800 transition-colors"
          >
            Apply
          </button>
          <button
            onClick={() => {
              setActionFilter('');
              setResourceTypeFilter('');
              setDateFrom('');
              setDateTo('');
              setSearch('');
              setPage(1);
            }}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-x-auto">
        {isLoading ? (
          <div className="flex justify-center py-16">
            <LoadingSpinner size="lg" />
          </div>
        ) : paginatedEntries.length === 0 ? (
          <p className="text-center text-gray-500 py-16">No audit log entries found.</p>
        ) : (
          <table className="min-w-full divide-y divide-gray-200 text-sm" role="table" aria-label="Audit log entries">
            <thead className="bg-gray-50">
              <tr>
                {['Timestamp', 'User ID', 'Action', 'Resource Type', 'Resource ID', 'Details'].map((col) => (
                  <th
                    key={col}
                    scope="col"
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {paginatedEntries.map((entry) => (
                <tr key={entry.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 whitespace-nowrap text-gray-700">{formatDate(entry.created_at)}</td>
                  <td className="px-4 py-3 whitespace-nowrap font-mono text-xs text-gray-500">
                    {entry.user_id ?? '—'}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-gray-900 font-medium">{entry.action}</td>
                  <td className="px-4 py-3 whitespace-nowrap text-gray-600">{entry.resource_type ?? '—'}</td>
                  <td className="px-4 py-3 whitespace-nowrap font-mono text-xs text-gray-500">
                    {entry.resource_id ?? '—'}
                  </td>
                  <td className="px-4 py-3 text-gray-600 max-w-xs truncate" title={formatDetails(entry.details)}>
                    {formatDetails(entry.details)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {!isLoading && totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-gray-600">
            Page {page} of {totalPages} ({filteredEntries.length} total)
          </p>
          <div className="flex gap-2" role="navigation" aria-label="Audit log pagination">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-40 hover:bg-gray-50 transition-colors"
              aria-label="Previous page"
            >
              ← Prev
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm disabled:opacity-40 hover:bg-gray-50 transition-colors"
              aria-label="Next page"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </main>
  );
};
