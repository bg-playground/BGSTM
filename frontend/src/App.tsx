import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { AuthProvider } from './components/AuthProvider';
import ProtectedRoute from './components/ProtectedRoute';
import AdminRoute from './components/AdminRoute';
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
            </Route>
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
