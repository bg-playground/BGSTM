import React from 'react';

type Role = 'admin' | 'reviewer' | 'viewer';

interface RoleBadgeProps {
  role: Role;
  className?: string;
}

const roleStyles: Record<Role, string> = {
  admin: 'bg-purple-100 text-purple-800 border-purple-200',
  reviewer: 'bg-blue-100 text-blue-800 border-blue-200',
  viewer: 'bg-gray-100 text-gray-700 border-gray-200',
};

export const RoleBadge: React.FC<RoleBadgeProps> = ({ role, className = '' }) => {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${roleStyles[role]} ${className}`}
    >
      {role}
    </span>
  );
};
