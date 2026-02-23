import React from 'react';
import { useRoleGate } from '../hooks/useRoleGate';

interface RoleGateProps {
  allowedRoles: string[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const RoleGate: React.FC<RoleGateProps> = ({ allowedRoles, children, fallback = null }) => {
  const { hasRole } = useRoleGate();
  return hasRole(allowedRoles) ? <>{children}</> : <>{fallback}</>;
};
