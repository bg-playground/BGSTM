import React from 'react';
import { Link } from 'react-router-dom';

const AccessDeniedPage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
      <div className="text-6xl font-bold text-red-500 mb-4">403</div>
      <h1 className="text-2xl font-semibold text-gray-800 mb-2">Access Denied</h1>
      <p className="text-gray-600 mb-6">You do not have permission to view this page. Admin access is required.</p>
      <Link to="/" className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
        Go to Dashboard
      </Link>
    </div>
  );
};

export default AccessDeniedPage;
