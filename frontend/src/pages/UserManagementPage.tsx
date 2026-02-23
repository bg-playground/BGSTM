import React, { useCallback, useEffect, useState } from 'react';
import { usersApi } from '../api/users';
import type { UserRecord } from '../api/users';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const ROLE_BADGE: Record<string, string> = {
  admin: 'bg-purple-100 text-purple-700',
  reviewer: 'bg-blue-100 text-blue-700',
  viewer: 'bg-gray-100 text-gray-700',
};

const RoleModal: React.FC<{
  user: UserRecord;
  onClose: () => void;
  onSave: (userId: string, role: 'admin' | 'reviewer' | 'viewer') => Promise<void>;
}> = ({ user, onClose, onSave }) => {
  const [role, setRole] = useState<'admin' | 'reviewer' | 'viewer'>(user.role);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    await onSave(user.id, role);
    setSaving(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl p-6 w-80">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Change Role</h2>
        <p className="text-sm text-gray-600 mb-4">
          User: <span className="font-medium">{user.full_name ?? user.email}</span>
        </p>
        <select
          value={role}
          onChange={(e) => setRole(e.target.value as 'admin' | 'reviewer' | 'viewer')}
          className="w-full border border-gray-300 rounded px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="admin">Admin</option>
          <option value="reviewer">Reviewer</option>
          <option value="viewer">Viewer</option>
        </select>
        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm rounded border border-gray-300 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving || role === user.role}
            className="px-4 py-2 text-sm rounded bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
};

const DeactivateDialog: React.FC<{
  user: UserRecord;
  onClose: () => void;
  onConfirm: () => Promise<void>;
}> = ({ user, onClose, onConfirm }) => {
  const [loading, setLoading] = useState(false);

  const handleConfirm = async () => {
    setLoading(true);
    await onConfirm();
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl p-6 w-80">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Deactivate User</h2>
        <p className="text-sm text-gray-600 mb-6">
          Are you sure you want to deactivate{' '}
          <span className="font-medium">{user.full_name ?? user.email}</span>? They will lose access
          to the system.
        </p>
        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm rounded border border-gray-300 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={loading}
            className="px-4 py-2 text-sm rounded bg-red-600 text-white hover:bg-red-700 disabled:opacity-50"
          >
            {loading ? 'Deactivating…' : 'Deactivate'}
          </button>
        </div>
      </div>
    </div>
  );
};

export const UserManagementPage: React.FC = () => {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [roleModalUser, setRoleModalUser] = useState<UserRecord | null>(null);
  const [deactivateUser, setDeactivateUser] = useState<UserRecord | null>(null);

  const { user: currentUser } = useAuth();
  const { showToast } = useToast();

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await usersApi.list();
      setUsers(data.users);
      setTotal(data.total);
    } catch {
      setError('Failed to load users');
      showToast('Failed to load users', 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleRoleChange = useCallback(
    async (userId: string, role: 'admin' | 'reviewer' | 'viewer') => {
      try {
        const updated = await usersApi.update(userId, { role });
        setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
        setRoleModalUser(null);
        showToast('Role updated successfully', 'success');
      } catch {
        showToast('Failed to update role', 'error');
      }
    },
    [showToast],
  );

  const handleToggleActive = useCallback(
    async (user: UserRecord) => {
      if (user.is_active) {
        // Show confirmation dialog for deactivation
        setDeactivateUser(user);
      } else {
        try {
          const updated = await usersApi.update(user.id, { is_active: true });
          setUsers((prev) => prev.map((u) => (u.id === user.id ? updated : u)));
          showToast('User activated successfully', 'success');
        } catch {
          showToast('Failed to activate user', 'error');
        }
      }
    },
    [showToast],
  );

  const handleConfirmDeactivate = useCallback(async () => {
    if (!deactivateUser) return;
    try {
      const updated = await usersApi.update(deactivateUser.id, { is_active: false });
      setUsers((prev) => prev.map((u) => (u.id === deactivateUser.id ? updated : u)));
      setDeactivateUser(null);
      showToast('User deactivated successfully', 'success');
    } catch {
      showToast('Failed to deactivate user', 'error');
    }
  }, [deactivateUser, showToast]);

  const filteredUsers = search
    ? users.filter(
        (u) =>
          (u.full_name ?? '').toLowerCase().includes(search.toLowerCase()) ||
          u.email.toLowerCase().includes(search.toLowerCase()),
      )
    : users;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">User Management</h1>

      {/* Search */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <input
          type="text"
          placeholder="Search by name or email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
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
              onClick={loadUsers}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No users found</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Username
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredUsers.map((u) => {
                    const isSelf = u.id === currentUser?.id;
                    return (
                      <tr key={u.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                          {u.full_name ?? '—'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                          {u.email}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <button
                            onClick={() => setRoleModalUser(u)}
                            className={`px-2 py-0.5 rounded text-xs font-semibold ${ROLE_BADGE[u.role]} hover:opacity-80`}
                          >
                            {u.role}
                          </button>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <span
                            className={`px-2 py-0.5 rounded text-xs font-semibold ${
                              u.is_active
                                ? 'bg-green-100 text-green-700'
                                : 'bg-red-100 text-red-700'
                            }`}
                          >
                            {u.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                          {new Date(u.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="flex gap-2">
                            <button
                              onClick={() => setRoleModalUser(u)}
                              className="text-xs px-2 py-1 rounded border border-gray-300 hover:bg-gray-50"
                            >
                              Edit role
                            </button>
                            <span title={isSelf ? 'You cannot deactivate yourself' : undefined}>
                              <button
                                onClick={() => handleToggleActive(u)}
                                disabled={isSelf}
                                className={`text-xs px-2 py-1 rounded border ${
                                  isSelf
                                    ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                                    : u.is_active
                                    ? 'border-red-300 text-red-600 hover:bg-red-50'
                                    : 'border-green-300 text-green-600 hover:bg-green-50'
                                }`}
                              >
                                {u.is_active ? 'Deactivate' : 'Activate'}
                              </button>
                            </span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <div className="px-4 py-3 border-t border-gray-200 text-sm text-gray-600">
              Total: <span className="font-medium">{total}</span> users
            </div>
          </>
        )}
      </div>

      {/* Role change modal */}
      {roleModalUser && (
        <RoleModal
          user={roleModalUser}
          onClose={() => setRoleModalUser(null)}
          onSave={handleRoleChange}
        />
      )}

      {/* Deactivate confirmation */}
      {deactivateUser && (
        <DeactivateDialog
          user={deactivateUser}
          onClose={() => setDeactivateUser(null)}
          onConfirm={handleConfirmDeactivate}
        />
      )}
    </div>
  );
};
