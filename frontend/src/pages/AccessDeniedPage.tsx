import React from 'react';
import { Link } from 'react-router-dom';

const AccessDeniedPage: React.FC = () => (
  <div className="flex flex-col items-center justify-center h-96 gap-4">
    <h1 className="text-4xl font-bold text-gray-800">403 – Access Denied</h1>
    <p className="text-gray-500">You do not have permission to view this page.</p>
    <Link to="/" className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
      Back to Dashboard
    </Link>
  </div>
);

export default AccessDeniedPage;
