import React from 'react';
import { useAuth } from '../context/AuthContext';

type Role = 'admin' | 'reviewer' | 'viewer';

interface RoleGateProps {
  allowedRoles: Role[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const RoleGate: React.FC<RoleGateProps> = ({ allowedRoles, children, fallback = null }) => {
  const { role } = useAuth();
  if (role && allowedRoles.includes(role as Role)) {
    return <>{children}</>;
  }
  return <>{fallback}</>;
};
