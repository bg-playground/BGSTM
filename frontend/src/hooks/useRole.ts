import { useAuth } from '../context/AuthContext';
import type { User } from '../types/auth';

export type Role = User['role'];

export const useRole = (): Role | null => {
  const { user } = useAuth();
  return user?.role ?? null;
};

export const useHasRole = (roles: Role[]): boolean => {
  const role = useRole();
  return role !== null && roles.includes(role);
};

export const useIsAdmin = (): boolean => useHasRole(['admin']);

export const useIsReviewer = (): boolean => useHasRole(['reviewer']);
