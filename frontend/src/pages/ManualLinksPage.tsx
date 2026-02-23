import React, { useCallback, useEffect, useState } from 'react';
import { linksApi } from '../api/links';
import { requirementsApi } from '../api/requirements';
import { testCasesApi } from '../api/testCases';
import { LinkSource, LinkType } from '../types/api';
import type { Link, LinkCreate, Requirement, TestCase } from '../types/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useToast } from '../context/ToastContext';
import RoleGate from '../components/RoleGate';

export const ManualLinksPage: React.FC = () => {
  const [links, setLinks] = useState<Link[]>([]);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState<LinkCreate>({
    requirement_id: '',
    test_case_id: '',
    link_type: LinkType.COVERS,
    link_source: LinkSource.MANUAL,
  });
  const { showToast } = useToast();

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [linksData, reqData, tcData] = await Promise.all([
        linksApi.list(),
        requirementsApi.list(1, 200),
        testCasesApi.list(1, 200),
      ]);
      setLinks(linksData.items);
      setRequirements(reqData.items);
      setTestCases(tcData.items);
    } catch (error) {
      console.error('Error loading data:', error);
      showToast('Failed to load data', 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await linksApi.create(formData);
      showToast('Link created successfully', 'success');
      setShowModal(false);
      resetForm();
      await loadData();
    } catch (error: unknown) {
      console.error('Error creating link:', error);
      const axiosError = error as { response?: { data?: { detail?: string } } };
      const message = axiosError?.response?.data?.detail ?? 'Failed to create link';
      showToast(message, 'error');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this link?')) return;
    
    try {
      await linksApi.delete(id);
      showToast('Link deleted successfully', 'success');
      await loadData();
    } catch (error) {
      console.error('Error deleting link:', error);
      showToast('Failed to delete link', 'error');
    }
  };

  const resetForm = () => {
    setFormData({
      requirement_id: '',
      test_case_id: '',
      link_type: LinkType.COVERS,
      link_source: LinkSource.MANUAL,
    });
  };

  const handleCancel = () => {
    setShowModal(false);
    resetForm();
  };

  const getRequirement = (id: string) => requirements.find((r) => r.id === id);
  const getTestCase = (id: string) => testCases.find((tc) => tc.id === id);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Manual Links</h1>
        <RoleGate allowedRoles={['admin', 'reviewer']}>
          <button
            onClick={() => setShowModal(true)}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            + New Link
          </button>
        </RoleGate>
      </div>

      {links.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <p className="text-gray-600 text-lg">No links yet</p>
          <p className="text-gray-500 text-sm mt-2">
            Click "New Link" to create a manual link between a requirement and test case
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {links.map((link) => {
            const requirement = getRequirement(link.requirement_id);
            const testCase = getTestCase(link.test_case_id);

            return (
              <div key={link.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="border-r pr-6">
                    <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                      Requirement
                    </h3>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">
                      {requirement?.title || 'Unknown'}
                    </h4>
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {requirement?.description || 'No description'}
                    </p>
                  </div>

                  <div className="pl-6">
                    <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                      Test Case
                    </h3>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">
                      {testCase?.title || 'Unknown'}
                    </h4>
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {testCase?.description || 'No description'}
                    </p>
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t flex items-center justify-between">
                  <div className="flex items-center gap-4 text-sm">
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-medium">
                      {link.link_type}
                    </span>
                    <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full font-medium">
                      {link.link_source}
                    </span>
                    {link.confidence_score && (
                      <span className="text-gray-600">
                        Confidence: {(link.confidence_score * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>

                  <RoleGate allowedRoles={['admin', 'reviewer']}>
                    <button
                      onClick={() => handleDelete(link.id)}
                      className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
                    >
                      Delete
                    </button>
                  </RoleGate>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-2xl w-full">
            <h2 className="text-2xl font-bold mb-6">Create New Link</h2>
            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Requirement *
                  </label>
                  <select
                    required
                    value={formData.requirement_id}
                    onChange={(e) => setFormData({ ...formData, requirement_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">Select a requirement</option>
                    {requirements.map((req) => (
                      <option key={req.id} value={req.id}>
                        {req.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Test Case *
                  </label>
                  <select
                    required
                    value={formData.test_case_id}
                    onChange={(e) => setFormData({ ...formData, test_case_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">Select a test case</option>
                    {testCases.map((tc) => (
                      <option key={tc.id} value={tc.id}>
                        {tc.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Link Type *
                  </label>
                  <select
                    value={formData.link_type}
                    onChange={(e) => setFormData({ ...formData, link_type: e.target.value as LinkType })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value={LinkType.COVERS}>Covers</option>
                    <option value={LinkType.VERIFIES}>Verifies</option>
                    <option value={LinkType.VALIDATES}>Validates</option>
                    <option value={LinkType.RELATED_TO}>Related To</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notes
                  </label>
                  <textarea
                    rows={3}
                    value={formData.notes || ''}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Optional notes about this link..."
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  type="button"
                  onClick={handleCancel}
                  className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  Create Link
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
