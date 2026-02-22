import React from 'react';
import { Navigate } from 'react-router-dom';
import { LoadingSpinner } from './LoadingSpinner';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <LoadingSpinner className="min-h-screen" size="lg" />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

export default ProtectedRoute;
