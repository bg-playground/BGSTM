import { useAuth } from '../context/AuthContext';

type Role = 'admin' | 'reviewer' | 'viewer';

export const useRoleGate = (allowedRoles: Role[]): { allowed: boolean } => {
  const { role } = useAuth();
  return { allowed: role !== null && allowedRoles.includes(role as Role) };
};
