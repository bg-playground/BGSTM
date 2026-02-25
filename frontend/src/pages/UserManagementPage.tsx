import React, { useCallback, useEffect, useState } from 'react';
import { usersApi } from '../api/users';
import type { ManagedUser } from '../api/users';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Pagination } from '../components/Pagination';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';

const PAGE_SIZE = 25;

const roleBadge: Record<string, string> = {
  admin: 'bg-red-100 text-red-800',
  reviewer: 'bg-blue-100 text-blue-800',
  viewer: 'bg-gray-100 text-gray-700',
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export const UserManagementPage: React.FC = () => {
  const { showToast } = useToast();
  const { user: currentUser } = useAuth();

  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');

  // Inline role-editing state
  const [editingRoleId, setEditingRoleId] = useState<string | null>(null);
  const [newRole, setNewRole] = useState<'admin' | 'reviewer' | 'viewer'>('viewer');

  const loadUsers = useCallback(
    async () => {
      try {
        setLoading(true);
        const res = await usersApi.list(0, 500);
        setTotal(res.data.total);
        setUsers(res.data.users);
      } catch {
        showToast('Failed to load users', 'error');
      } finally {
        setLoading(false);
      }
    },
    [showToast],
  );

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  // Client-side search/filter
  const filtered = users.filter((u) => {
    const q = search.toLowerCase();
    const matchesSearch =
      !q ||
      u.email.toLowerCase().includes(q) ||
      (u.full_name?.toLowerCase().includes(q) ?? false);
    const matchesRole = !roleFilter || u.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const filteredPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));

  const roleCounts = {
    admin: users.filter((u) => u.role === 'admin').length,
    reviewer: users.filter((u) => u.role === 'reviewer').length,
    viewer: users.filter((u) => u.role === 'viewer').length,
  };

  const handleStartEditRole = useCallback((u: ManagedUser) => {
    setEditingRoleId(u.id);
    setNewRole(u.role);
  }, []);

  const handleSaveRole = useCallback(
    async (userId: string) => {
      try {
        await usersApi.update(userId, { role: newRole });
        showToast('Role updated', 'success');
        setEditingRoleId(null);
        await loadUsers();
      } catch {
        showToast('Failed to update role', 'error');
      }
    },
    [newRole, loadUsers, showToast],
  );

  const handleToggleActive = useCallback(
    async (u: ManagedUser) => {
      try {
        await usersApi.update(u.id, { is_active: !u.is_active });
        showToast(`User ${u.is_active ? 'deactivated' : 'activated'}`, 'success');
        await loadUsers();
      } catch {
        showToast('Failed to update user status', 'error');
      }
    },
    [loadUsers, showToast],
  );

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
          {!loading && (
            <p className="text-sm text-gray-500 mt-1">
              {total} users — {roleCounts.admin} admin{roleCounts.admin !== 1 ? 's' : ''},{' '}
              {roleCounts.reviewer} reviewer{roleCounts.reviewer !== 1 ? 's' : ''},{' '}
              {roleCounts.viewer} viewer{roleCounts.viewer !== 1 ? 's' : ''}
            </p>
          )}
        </div>
      </div>

      {/* Search/filter bar */}
      <div className="bg-white rounded-lg shadow p-4 mb-6 flex flex-wrap gap-4">
        <input
          type="text"
          placeholder="Search by name or email…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="flex-1 min-w-[200px] px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-primary-500 focus:border-primary-500"
        />
        <select
          value={roleFilter}
          onChange={(e) => {
            setRoleFilter(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="">All roles</option>
          <option value="admin">Admin</option>
          <option value="reviewer">Reviewer</option>
          <option value="viewer">Viewer</option>
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-16">
          <LoadingSpinner size="lg" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-10 text-center">
          <p className="text-gray-500">No users found.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Username', 'Email', 'Role', 'Status', 'Created', 'Last Updated', 'Actions'].map(
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
              {paginated.map((u) => {
                const isSelf = currentUser?.id === u.id;
                return (
                  <tr key={u.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900 whitespace-nowrap">
                      {u.full_name ?? '—'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700 whitespace-nowrap">{u.email}</td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {editingRoleId === u.id ? (
                        <div className="flex items-center gap-2">
                          <select
                            value={newRole}
                            onChange={(e) =>
                              setNewRole(e.target.value as 'admin' | 'reviewer' | 'viewer')
                            }
                            className="px-2 py-1 border border-gray-300 rounded text-sm"
                          >
                            <option value="admin">admin</option>
                            <option value="reviewer">reviewer</option>
                            <option value="viewer">viewer</option>
                          </select>
                          <button
                            onClick={() => handleSaveRole(u.id)}
                            className="text-xs px-2 py-1 bg-primary-600 text-white rounded hover:bg-primary-700"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingRoleId(null)}
                            className="text-xs px-2 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <span
                          className={`px-2 py-0.5 text-xs font-semibold rounded-full ${roleBadge[u.role]}`}
                        >
                          {u.role}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span
                        className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                          u.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
                      {formatDate(u.created_at)}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
                      {formatDate(u.updated_at)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        {editingRoleId !== u.id && (
                          <button
                            onClick={() => handleStartEditRole(u)}
                            className="text-xs px-2 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded hover:bg-blue-100"
                          >
                            Edit Role
                          </button>
                        )}
                        <button
                          onClick={() => handleToggleActive(u)}
                          disabled={isSelf}
                          title={isSelf ? 'Cannot deactivate your own account' : undefined}
                          className={`text-xs px-2 py-1 rounded border ${
                            isSelf
                              ? 'opacity-40 cursor-not-allowed border-gray-200 text-gray-400'
                              : u.is_active
                                ? 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100'
                                : 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100'
                          }`}
                        >
                          {u.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} pages={filteredPages} total={filtered.length} onPageChange={setPage} />
    </div>
  );
};
