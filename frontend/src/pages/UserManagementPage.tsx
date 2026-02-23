import React, { useCallback, useEffect, useState } from 'react';
import { adminApi } from '../api/adminApi';
import type { AdminUser } from '../api/adminApi';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Pagination } from '../components/Pagination';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const PAGE_SIZES = [10, 25, 50, 100];

const roleBadge: Record<string, string> = {
  admin: 'bg-red-100 text-red-800',
  reviewer: 'bg-blue-100 text-blue-800',
  viewer: 'bg-gray-100 text-gray-700',
};

export const UserManagementPage: React.FC = () => {
  const [allUsers, setAllUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [pendingRole, setPendingRole] = useState<Record<string, string>>({});
  const { user: currentUser } = useAuth();
  const { showToast } = useToast();

  const total = allUsers.length;
  const pages = Math.ceil(total / pageSize);
  const pagedUsers = allUsers.slice((page - 1) * pageSize, page * pageSize);

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      const res = await adminApi.getUsers(0, 500);
      setAllUsers(res.data.users);
    } catch {
      showToast('Failed to load users', 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleRoleChange = useCallback(
    async (userId: string, newRole: string) => {
      if (!confirm(`Change this user's role to "${newRole}"?`)) return;
      try {
        await adminApi.updateUser(userId, { role: newRole as AdminUser['role'] });
        showToast('Role updated successfully', 'success');
        await loadUsers();
      } catch {
        showToast('Failed to update role', 'error');
      } finally {
        setPendingRole((prev) => {
          const next = { ...prev };
          delete next[userId];
          return next;
        });
      }
    },
    [loadUsers, showToast],
  );

  const handleToggleActive = useCallback(
    async (userId: string, isActive: boolean) => {
      const action = isActive ? 'deactivate' : 'activate';
      if (!confirm(`Are you sure you want to ${action} this user?`)) return;
      try {
        await adminApi.updateUser(userId, { is_active: !isActive });
        showToast(`User ${action}d successfully`, 'success');
        await loadUsers();
      } catch {
        showToast(`Failed to ${action} user`, 'error');
      }
    },
    [loadUsers, showToast],
  );

  const isSelf = (userId: string) => currentUser?.id === userId;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-600">Page size:</label>
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setPage(1);
            }}
            className="px-2 py-1.5 text-sm border border-gray-300 rounded"
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
      ) : allUsers.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-500">No users found.</div>
      ) : (
        <div className="overflow-x-auto bg-white rounded-lg shadow">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                {['Name', 'Email', 'Role', 'Status', 'Created At', 'Actions'].map((h) => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {pagedUsers.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{u.full_name ?? '—'}</td>
                  <td className="px-4 py-3 text-gray-700">{u.email}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${roleBadge[u.role] ?? 'bg-gray-100 text-gray-700'}`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{new Date(u.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {/* Role change */}
                      <select
                        value={pendingRole[u.id] ?? u.role}
                        disabled={isSelf(u.id)}
                        title={isSelf(u.id) ? 'Cannot modify your own account' : undefined}
                        onChange={(e) => {
                          const newRole = e.target.value;
                          setPendingRole((prev) => ({ ...prev, [u.id]: newRole }));
                          handleRoleChange(u.id, newRole);
                        }}
                        className="px-2 py-1 text-xs border border-gray-300 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <option value="admin">admin</option>
                        <option value="reviewer">reviewer</option>
                        <option value="viewer">viewer</option>
                      </select>
                      {/* Toggle active */}
                      <button
                        onClick={() => handleToggleActive(u.id, u.is_active)}
                        disabled={isSelf(u.id)}
                        title={isSelf(u.id) ? 'Cannot modify your own account' : u.is_active ? 'Deactivate' : 'Activate'}
                        className={`px-3 py-1 text-xs rounded font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                          u.is_active
                            ? 'bg-red-100 text-red-700 hover:bg-red-200'
                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                        }`}
                      >
                        {u.is_active ? 'Deactivate' : 'Activate'}
                      </button>
                    </div>
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
