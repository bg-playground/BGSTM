import React, { useCallback, useEffect, useState } from 'react';
import { authApi } from '../api/auth';
import { TOKEN_STORAGE_KEY } from '../api/client';
import { AuthContext } from '../context/AuthContext';
import type { User } from '../types/auth';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_STORAGE_KEY));
  // Start loading only if there's a stored token to validate
  const [isLoading, setIsLoading] = useState(() => !!localStorage.getItem(TOKEN_STORAGE_KEY));

  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!storedToken) return;
    authApi
      .me()
      .then((res) => {
        setUser(res.data);
        setToken(storedToken);
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        setToken(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    const handleUnauthorized = () => {
      setToken(null);
      setUser(null);
    };
    window.addEventListener('bgstm-unauthorized', handleUnauthorized);
    return () => window.removeEventListener('bgstm-unauthorized', handleUnauthorized);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const tokenRes = await authApi.login({ email, password });
    const accessToken = tokenRes.data.access_token;
    localStorage.setItem(TOKEN_STORAGE_KEY, accessToken);
    setToken(accessToken);
    const meRes = await authApi.me();
    setUser(meRes.data);
  }, []);

  const register = useCallback(
    async (email: string, password: string, fullName?: string) => {
      await authApi.register({ email, password, full_name: fullName });
      await login(email, password);
    },
    [login],
  );

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        role: user?.role ?? null,
        isAdmin: user?.role === 'admin',
        isReviewer: user?.role === 'reviewer',
        isViewer: user?.role === 'viewer',
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
