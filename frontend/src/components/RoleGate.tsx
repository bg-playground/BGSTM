import React from 'react';
import { useHasRole } from '../hooks/useRole';
import type { Role } from '../hooks/useRole';

interface RoleGateProps {
  allowedRoles: Role[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const RoleGate: React.FC<RoleGateProps> = ({ allowedRoles, children, fallback = null }) => {
  const hasRole = useHasRole(allowedRoles);
  return hasRole ? <>{children}</> : <>{fallback}</>;
};
