import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { ToastProvider } from './components/Toast';
import { SuggestionDashboard } from './pages/SuggestionDashboard';
import { RequirementsPage } from './pages/RequirementsPage';
import { TestCasesPage } from './pages/TestCasesPage';
import { ManualLinksPage } from './pages/ManualLinksPage';

function App() {
  return (
    <ToastProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
          <Navigation />
          <Routes>
            <Route path="/" element={<SuggestionDashboard />} />
            <Route path="/requirements" element={<RequirementsPage />} />
            <Route path="/test-cases" element={<TestCasesPage />} />
            <Route path="/links" element={<ManualLinksPage />} />
          </Routes>
        </div>
      </BrowserRouter>
    </ToastProvider>
  );
}

export default App;
