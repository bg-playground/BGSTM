import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { adminApi } from '../api/admin';
import type { AdminUser } from '../api/admin';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';

const PAGE_SIZE = 20;

type SortField = 'email' | 'role' | 'created_at' | 'is_active';
type SortOrder = 'asc' | 'desc';

const roleBadgeColor: Record<AdminUser['role'], string> = {
  admin: 'bg-red-100 text-red-800',
  reviewer: 'bg-yellow-100 text-yellow-800',
  viewer: 'bg-blue-100 text-blue-800',
};

interface ConfirmDialog {
  type: 'role' | 'deactivate';
  user: AdminUser;
  newRole?: AdminUser['role'];
}

export const UserManagementPage: React.FC = () => {
  const { showToast } = useToast();
  const { user: currentUser } = useAuth();

  const [allUsers, setAllUsers] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [confirm, setConfirm] = useState<ConfirmDialog | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await adminApi.fetchUsers({ skip: 0, limit: 500 });
      setAllUsers(data.users);
      setTotal(data.total);
    } catch {
      showToast('Failed to load users', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    load();
  }, [load]);

  const filteredAndSorted = useMemo(() => {
    let result = allUsers;
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      result = result.filter(
        (u) => u.email.toLowerCase().includes(q) || (u.full_name ?? '').toLowerCase().includes(q)
      );
    }
    result = [...result].sort((a, b) => {
      let aVal: string | boolean = a[sortField];
      let bVal: string | boolean = b[sortField];
      if (typeof aVal === 'boolean') {
        aVal = aVal ? '1' : '0';
        bVal = (bVal as boolean) ? '1' : '0';
      }
      const cmp = String(aVal).localeCompare(String(bVal));
      return sortOrder === 'asc' ? cmp : -cmp;
    });
    return result;
  }, [allUsers, search, sortField, sortOrder]);

  const paginated = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE;
    return filteredAndSorted.slice(start, start + PAGE_SIZE);
  }, [filteredAndSorted, page]);

  const totalPages = Math.max(1, Math.ceil(filteredAndSorted.length / PAGE_SIZE));

  const handleSort = useCallback(
    (field: SortField) => {
      if (sortField === field) {
        setSortOrder((o) => (o === 'asc' ? 'desc' : 'asc'));
      } else {
        setSortField(field);
        setSortOrder('asc');
      }
      setPage(1);
    },
    [sortField]
  );

  const handleConfirmAction = useCallback(async () => {
    if (!confirm) return;
    setActionLoading(true);
    try {
      if (confirm.type === 'role' && confirm.newRole) {
        const updated = await adminApi.updateUserRole(confirm.user.id, confirm.newRole);
        setAllUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
        showToast(`Role updated to "${confirm.newRole}"`, 'success');
      } else if (confirm.type === 'deactivate') {
        const updated = await adminApi.deactivateUser(confirm.user.id);
        setAllUsers((prev) => prev.map((u) => (u.id === updated.id ? updated : u)));
        showToast('User deactivated', 'success');
      }
    } catch {
      showToast('Action failed', 'error');
    } finally {
      setActionLoading(false);
      setConfirm(null);
    }
  }, [confirm, showToast]);

  const sortIcon = (field: SortField) => {
    if (sortField !== field) return <span className="text-gray-300 ml-1">↕</span>;
    return <span className="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>;
  };

  return (
    <main className="container mx-auto px-4 py-8" aria-label="User Management">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
        <span className="text-sm text-gray-500">{total} total users</span>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <label htmlFor="user-search" className="block text-xs font-medium text-gray-700 mb-1">
          Search users
        </label>
        <input
          id="user-search"
          type="search"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          placeholder="Search by name or email…"
          className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-x-auto">
        {isLoading ? (
          <div className="flex justify-center py-16">
            <LoadingSpinner size="lg" />
          </div>
        ) : paginated.length === 0 ? (
          <p className="text-center text-gray-500 py-16">No users found.</p>
        ) : (
          <table className="min-w-full divide-y divide-gray-200 text-sm" role="table" aria-label="Users table">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Username / Email
                </th>
                <th
                  scope="col"
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  onClick={() => handleSort('role')}
                  aria-sort={sortField === 'role' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
                >
                  Role {sortIcon('role')}
                </th>
                <th
                  scope="col"
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  onClick={() => handleSort('created_at')}
                  aria-sort={sortField === 'created_at' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
                >
                  Created At {sortIcon('created_at')}
                </th>
                <th
                  scope="col"
                  className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
                  onClick={() => handleSort('is_active')}
                  aria-sort={sortField === 'is_active' ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none'}
                >
                  Status {sortIcon('is_active')}
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {paginated.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-900">{u.full_name ?? u.email}</p>
                    {u.full_name && <p className="text-xs text-gray-500">{u.email}</p>}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${roleBadgeColor[u.role]}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-gray-600">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                        u.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-500'
                      }`}
                    >
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      {/* Role selector */}
                      <select
                        aria-label={`Change role for ${u.email}`}
                        value={u.role}
                        disabled={u.id === currentUser?.id}
                        onChange={(e) =>
                          setConfirm({
                            type: 'role',
                            user: u,
                            newRole: e.target.value as AdminUser['role'],
                          })
                        }
                        className="border border-gray-300 rounded-md px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
                      >
                        <option value="admin">admin</option>
                        <option value="reviewer">reviewer</option>
                        <option value="viewer">viewer</option>
                      </select>
                      {/* Deactivate button */}
                      {u.is_active && u.id !== currentUser?.id && (
                        <button
                          onClick={() => setConfirm({ type: 'deactivate', user: u })}
                          className="px-2 py-1 text-xs text-red-600 border border-red-200 rounded-md hover:bg-red-50 transition-colors"
                          aria-label={`Deactivate ${u.email}`}
                        >
                          Deactivate
                        </button>
                      )}
                    </div>
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
            Page {page} of {totalPages} ({filteredAndSorted.length} users)
          </p>
          <div className="flex gap-2" role="navigation" aria-label="User list pagination">
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

      {/* Confirmation Dialog */}
      {confirm && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          role="dialog"
          aria-modal="true"
          aria-labelledby="confirm-dialog-title"
        >
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-sm w-full mx-4">
            <h2 id="confirm-dialog-title" className="text-lg font-semibold text-gray-900 mb-3">
              {confirm.type === 'deactivate' ? 'Deactivate User' : 'Change Role'}
            </h2>
            <p className="text-sm text-gray-600 mb-6">
              {confirm.type === 'deactivate'
                ? `Are you sure you want to deactivate "${confirm.user.full_name ?? confirm.user.email}"?`
                : `Change role of "${confirm.user.full_name ?? confirm.user.email}" to "${confirm.newRole}"?`}
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setConfirm(null)}
                disabled={actionLoading}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmAction}
                disabled={actionLoading}
                className={`px-4 py-2 rounded-md text-sm font-medium text-white transition-colors disabled:opacity-50 ${
                  confirm.type === 'deactivate' ? 'bg-red-600 hover:bg-red-700' : 'bg-primary-700 hover:bg-primary-800'
                }`}
              >
                {actionLoading ? 'Processing…' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
};
