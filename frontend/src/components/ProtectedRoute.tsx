import React from 'react';
import { Navigate } from 'react-router-dom';
import { LoadingSpinner } from './LoadingSpinner';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute: React.FC<{ children: React.ReactNode; requiredRole?: 'admin' }> = ({
  children,
  requiredRole,
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  if (isLoading) return <LoadingSpinner className="min-h-screen" size="lg" />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (requiredRole && user?.role !== requiredRole) return <Navigate to="/403" replace />;
  return <>{children}</>;
};

export default ProtectedRoute;
