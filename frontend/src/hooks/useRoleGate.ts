import { useAuth } from '../context/AuthContext';

export interface UseRoleGateResult {
  role: string;
  isAdmin: boolean;
  isReviewer: boolean;
  isViewer: boolean;
  hasRole: (roles: string[]) => boolean;
}

export function useRoleGate(): UseRoleGateResult {
  const { user } = useAuth();
  const role = user?.role ?? 'viewer';

  return {
    role,
    isAdmin: role === 'admin',
    isReviewer: role === 'reviewer',
    isViewer: role === 'viewer',
    hasRole: (roles: string[]) => roles.includes(role),
  };
}
