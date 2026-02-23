import React, { useCallback, useEffect, useState } from 'react';
import { usersApi } from '../api/users';
import type { UserResponse } from '../api/users';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Pagination } from '../components/Pagination';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const PAGE_SIZE = 20;

const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

const roleBadge: Record<string, string> = {
  admin: 'bg-red-100 text-red-800',
  reviewer: 'bg-yellow-100 text-yellow-800',
  viewer: 'bg-blue-100 text-blue-800',
};

const UserManagementPage: React.FC = () => {
  const { user: currentUser } = useAuth();
  const { showToast } = useToast();

  const [allUsers, setAllUsers] = useState<UserResponse[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [search, setSearch] = useState('');

  // Confirmation dialog state
  const [confirmDialog, setConfirmDialog] = useState<{
    userId: string;
    action: 'role' | 'status';
    newRole?: 'admin' | 'reviewer' | 'viewer';
    newStatus?: boolean;
    label: string;
  } | null>(null);

  const [saving, setSaving] = useState(false);

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(false);
      const data = await usersApi.list(0, 500);
      setAllUsers(data.users);
    } catch {
      setError(true);
      showToast('Failed to load users', 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const filteredUsers = allUsers.filter(
    (u) =>
      u.email.toLowerCase().includes(search.toLowerCase()) ||
      (u.full_name ?? '').toLowerCase().includes(search.toLowerCase()),
  );

  const pages = Math.max(1, Math.ceil(filteredUsers.length / PAGE_SIZE));
  const pagedUsers = filteredUsers.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const handleRoleChange = (userId: string, newRole: 'admin' | 'reviewer' | 'viewer') => {
    setConfirmDialog({
      userId,
      action: 'role',
      newRole,
      label: `Change role to "${newRole}"?`,
    });
  };

  const handleToggleStatus = (user: UserResponse) => {
    const newStatus = !user.is_active;
    setConfirmDialog({
      userId: user.id,
      action: 'status',
      newStatus,
      label: newStatus ? 'Activate this user?' : 'Deactivate this user?',
    });
  };

  const handleConfirm = async () => {
    if (!confirmDialog) return;
    setSaving(true);
    try {
      if (confirmDialog.action === 'role' && confirmDialog.newRole) {
        await usersApi.update(confirmDialog.userId, { role: confirmDialog.newRole });
        showToast('Role updated successfully', 'success');
      } else if (confirmDialog.action === 'status' && confirmDialog.newStatus !== undefined) {
        if (!confirmDialog.newStatus) {
          await usersApi.deactivate(confirmDialog.userId);
        } else {
          await usersApi.update(confirmDialog.userId, { is_active: true });
        }
        showToast(
          confirmDialog.newStatus ? 'User activated successfully' : 'User deactivated successfully',
          'success',
        );
      }
      await loadUsers();
    } catch {
      showToast('Failed to update user', 'error');
    } finally {
      setSaving(false);
      setConfirmDialog(null);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">User Management</h1>

      {/* Search */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <input
          type="text"
          placeholder="Search by name or email…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          className="w-full sm:w-80 px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
        />
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <LoadingSpinner size="lg" />
        </div>
      ) : error ? (
        <div className="bg-red-50 rounded-lg p-8 text-center">
          <p className="text-red-700 font-medium mb-3">Failed to load users.</p>
          <button
            onClick={loadUsers}
            className="px-5 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      ) : filteredUsers.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <p className="text-gray-600 text-lg">No users match your search.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  User
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {pagedUsers.map((u) => {
                const isSelf = u.id === currentUser?.id;
                return (
                  <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="text-sm font-medium text-gray-900">{u.full_name ?? u.email}</div>
                      {u.full_name && <div className="text-xs text-gray-500">{u.email}</div>}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-semibold ${roleBadge[u.role] ?? 'bg-gray-100 text-gray-800'}`}
                      >
                        {u.role}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-semibold ${
                          u.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-500'
                        }`}
                      >
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
                      {formatDate(u.created_at)}
                    </td>
                    <td className="px-4 py-3">
                      {isSelf ? (
                        <span className="text-xs text-gray-400 italic">You</span>
                      ) : (
                        <div className="flex items-center gap-2">
                          <select
                            value={u.role}
                            onChange={(e) =>
                              handleRoleChange(u.id, e.target.value as 'admin' | 'reviewer' | 'viewer')
                            }
                            className="text-sm px-2 py-1 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                          >
                            <option value="admin">admin</option>
                            <option value="reviewer">reviewer</option>
                            <option value="viewer">viewer</option>
                          </select>
                          <button
                            onClick={() => handleToggleStatus(u)}
                            className={`text-xs px-3 py-1 rounded-md font-medium transition-colors ${
                              u.is_active
                                ? 'bg-red-100 text-red-700 hover:bg-red-200'
                                : 'bg-green-100 text-green-700 hover:bg-green-200'
                            }`}
                          >
                            {u.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} pages={pages} total={filteredUsers.length} onPageChange={setPage} />

      {/* Confirmation Dialog */}
      {confirmDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl p-8 max-w-sm w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Confirm Action</h3>
            <p className="text-gray-600 mb-6">{confirmDialog.label}</p>
            <div className="flex gap-3">
              <button
                onClick={() => setConfirmDialog(null)}
                disabled={saving}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirm}
                disabled={saving}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
              >
                {saving ? 'Saving…' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagementPage;
