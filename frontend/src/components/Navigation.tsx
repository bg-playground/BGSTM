import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { NotificationBell } from './NotificationBell';

export const Navigation: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const navItems = [
    { path: '/', label: 'Suggestion Dashboard' },
    { path: '/requirements', label: 'Requirements' },
    { path: '/test-cases', label: 'Test Cases' },
    { path: '/links', label: 'Manual Links' },
    { path: '/traceability', label: 'Traceability Matrix' },
    { path: '/metrics', label: 'Metrics' },
    ...(user?.role === 'admin'
      ? [
          { path: '/admin/audit-log', label: 'Audit Log' },
          { path: '/admin/users', label: 'Users' },
        ]
      : []),
  ];

  const roleBadgeColor = {
    admin: 'bg-red-500',
    reviewer: 'bg-yellow-500',
    viewer: 'bg-blue-500',
  } as const;

  return (
    <nav className="bg-primary-700 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold">BGSTM Traceability</h1>
          </div>
          <div className="flex space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === item.path
                    ? 'bg-primary-800 text-white'
                    : 'text-gray-200 hover:bg-primary-600 hover:text-white'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
          {user && (
            <div className="flex items-center space-x-3">
              <NotificationBell />
              <span
                className={`text-xs font-semibold px-2 py-0.5 rounded-full text-white ${roleBadgeColor[user.role]}`}
              >
                {user.role}
              </span>
              <span className="text-sm text-gray-200 max-w-[160px] truncate">
                {user.full_name ?? user.email}
              </span>
              <button
                onClick={logout}
                className="text-sm text-gray-300 hover:text-white border border-gray-500 hover:border-white px-3 py-1 rounded-md transition-colors"
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};
