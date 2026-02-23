import { createContext, useContext } from 'react';
import type { User } from '../types/auth';

export interface AuthContextValue {
  user: User | null;
  token: string | null;
  role: 'admin' | 'reviewer' | 'viewer' | null;
  isAdmin: boolean;
  isReviewer: boolean;
  isViewer: boolean;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
