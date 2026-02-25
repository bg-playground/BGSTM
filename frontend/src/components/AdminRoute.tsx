import React from 'react';
import { Navigate } from 'react-router-dom';
import { LoadingSpinner } from './LoadingSpinner';
import { useAuth } from '../context/AuthContext';

const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <LoadingSpinner className="min-h-screen" size="lg" />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.role !== 'admin') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">403</h1>
        <p className="text-lg text-gray-600">Access Denied — Admin only.</p>
      </div>
    );
  }
  return <>{children}</>;
};

export default AdminRoute;
