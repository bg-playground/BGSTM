import React from 'react';
import { BrowserRouter, Routes, Route, Outlet, Navigate } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { AuthProvider } from './components/AuthProvider';
import ProtectedRoute from './components/ProtectedRoute';
import { ToastProvider } from './components/Toast';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { SuggestionDashboard } from './pages/SuggestionDashboard';
import { RequirementsPage } from './pages/RequirementsPage';
import { TestCasesPage } from './pages/TestCasesPage';
import { ManualLinksPage } from './pages/ManualLinksPage';
import TraceabilityMatrixPage from './pages/TraceabilityMatrixPage';
import MetricsDashboardPage from './pages/MetricsDashboardPage';
import { AuditLogPage } from './pages/AuditLogPage';
import { UserManagementPage } from './pages/UserManagementPage';
import { useAuth } from './context/AuthContext';

function ProtectedLayout() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <Outlet />
      </div>
    </ProtectedRoute>
  );
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  if (isLoading) return null;
  if (user?.role !== 'admin') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Access Denied</h2>
        <p className="text-gray-600">You need admin privileges to view this page.</p>
      </div>
    );
  }
  return <>{children}</>;
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route element={<ProtectedLayout />}>
              <Route path="/" element={<SuggestionDashboard />} />
              <Route path="/requirements" element={<RequirementsPage />} />
              <Route path="/test-cases" element={<TestCasesPage />} />
              <Route path="/links" element={<ManualLinksPage />} />
              <Route path="/traceability" element={<TraceabilityMatrixPage />} />
              <Route path="/metrics" element={<MetricsDashboardPage />} />
              <Route
                path="/admin/audit-log"
                element={
                  <AdminRoute>
                    <AuditLogPage />
                  </AdminRoute>
                }
              />
              <Route
                path="/admin/users"
                element={
                  <AdminRoute>
                    <UserManagementPage />
                  </AdminRoute>
                }
              />
              <Route path="/admin" element={<Navigate to="/admin/audit-log" replace />} />
            </Route>
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
