import React, { useCallback, useEffect, useState } from 'react';
import { adminApi } from '../api/admin';
import type { AdminUser } from '../api/admin';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { RoleBadge } from '../components/RoleBadge';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';

type Role = AdminUser['role'];

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—';
  try {
    return new Date(dateStr).toLocaleString();
  } catch {
    return dateStr;
  }
}

export const UserManagementPage: React.FC = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [confirmDeactivate, setConfirmDeactivate] = useState<AdminUser | null>(null);
  const [editingRoleUserId, setEditingRoleUserId] = useState<string | null>(null);
  const [pendingRole, setPendingRole] = useState<Role>('viewer');

  const { showToast } = useToast();
  const { user: currentUser } = useAuth();

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await adminApi.getUsers();
      setUsers(data);
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 401 || status === 403) {
        showToast('Access denied. Admin role required.', 'error');
      } else {
        showToast('Failed to load users', 'error');
      }
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const filteredUsers = users.filter((u) => {
    const q = search.toLowerCase();
    return u.email.toLowerCase().includes(q) || (u.full_name ?? '').toLowerCase().includes(q);
  });

  const handleDeactivate = useCallback(async () => {
    if (!confirmDeactivate) return;
    try {
      await adminApi.deleteUser(confirmDeactivate.id);
      showToast(`User ${confirmDeactivate.email} deactivated`, 'success');
      setConfirmDeactivate(null);
      await loadUsers();
    } catch {
      showToast('Failed to deactivate user', 'error');
    }
  }, [confirmDeactivate, showToast, loadUsers]);

  const handleOpenRoleEdit = useCallback((u: AdminUser) => {
    setEditingRoleUserId(u.id);
    setPendingRole(u.role);
  }, []);

  const handleSaveRole = useCallback(
    async (userId: string) => {
      try {
        await adminApi.updateUserRole(userId, pendingRole);
        showToast('Role updated successfully', 'success');
        setEditingRoleUserId(null);
        await loadUsers();
      } catch {
        showToast('Failed to update role', 'error');
      }
    },
    [pendingRole, showToast, loadUsers],
  );

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">User Management</h1>

      {/* Search */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name or email..."
          className="w-full max-w-md border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-16">
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <p className="text-lg font-medium">No users found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created At
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Login
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredUsers.map((u) => {
                  const isSelf = currentUser?.id === u.id;
                  return (
                    <tr key={u.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {u.full_name ?? '—'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{u.email}</td>
                      <td className="px-4 py-3 text-sm">
                        {editingRoleUserId === u.id ? (
                          <div className="flex items-center gap-2">
                            <select
                              value={pendingRole}
                              onChange={(e) => setPendingRole(e.target.value as Role)}
                              className="border border-gray-300 rounded px-2 py-1 text-xs"
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
                              onClick={() => setEditingRoleUserId(null)}
                              className="text-xs px-2 py-1 border border-gray-300 rounded hover:bg-gray-50"
                            >
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <RoleBadge role={u.role} />
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
                        {formatDate(u.created_at)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
                        {formatDate(u.last_login)}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                            u.is_active
                              ? 'bg-green-100 text-green-700'
                              : 'bg-red-100 text-red-700'
                          }`}
                        >
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleOpenRoleEdit(u)}
                            disabled={isSelf}
                            title={isSelf ? 'Cannot change your own role' : 'Edit role'}
                            className="text-xs px-2 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                          >
                            Edit Role
                          </button>
                          <button
                            onClick={() => setConfirmDeactivate(u)}
                            disabled={isSelf || !u.is_active}
                            title={
                              isSelf
                                ? 'Cannot deactivate yourself'
                                : !u.is_active
                                  ? 'User already inactive'
                                  : 'Deactivate user'
                            }
                            className="text-xs px-2 py-1 border border-red-300 text-red-600 rounded hover:bg-red-50 disabled:opacity-40 disabled:cursor-not-allowed"
                          >
                            Deactivate
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
      </div>

      <ConfirmDialog
        isOpen={!!confirmDeactivate}
        title="Deactivate User"
        message={`Are you sure you want to deactivate ${confirmDeactivate?.email}? They will no longer be able to log in.`}
        confirmLabel="Deactivate"
        onConfirm={handleDeactivate}
        onCancel={() => setConfirmDeactivate(null)}
        variant="danger"
      />
    </div>
  );
};
