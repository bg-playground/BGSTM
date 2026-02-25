import React, { useCallback, useEffect, useState } from 'react';
import { testCasesApi } from '../api/testCases';
import { TestCaseType, PriorityLevel, TestCaseStatus } from '../types/api';
import type { TestCase, TestCaseCreate, TestCaseUpdate } from '../types/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Pagination } from '../components/Pagination';
import { useToast } from '../context/ToastContext';
import { useRoleGate } from '../hooks/useRoleGate';

export const TestCasesPage: React.FC = () => {
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(0);
  const PAGE_SIZE = 50;
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState<TestCaseCreate>({
    title: '',
    description: '',
    type: TestCaseType.FUNCTIONAL,
    priority: PriorityLevel.MEDIUM,
    status: TestCaseStatus.DRAFT,
    automated: false,
  });
  const { showToast } = useToast();
  const { isAdmin } = useRoleGate();

  const loadTestCases = useCallback(async (targetPage = page) => {
    try {
      setLoading(true);
      const data = await testCasesApi.list(targetPage, PAGE_SIZE);
      setTestCases(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (error) {
      console.error('Error loading test cases:', error);
      showToast('Failed to load test cases', 'error');
    } finally {
      setLoading(false);
    }
  }, [page, showToast]);

  useEffect(() => {
    loadTestCases(page);
  }, [page, loadTestCases]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await testCasesApi.update(editingId, formData as TestCaseUpdate);
        showToast('Test case updated successfully', 'success');
      } else {
        await testCasesApi.create(formData);
        showToast('Test case created successfully', 'success');
      }
      setShowModal(false);
      setEditingId(null);
      resetForm();
      await loadTestCases(page);
    } catch (error) {
      console.error('Error saving test case:', error);
      showToast('Failed to save test case', 'error');
    }
  };

  const handleEdit = (testCase: TestCase) => {
    setEditingId(testCase.id);
    setFormData({
      title: testCase.title,
      description: testCase.description,
      type: testCase.type,
      priority: testCase.priority,
      status: testCase.status,
      module: testCase.module,
      tags: testCase.tags,
      automated: testCase.automated,
      preconditions: testCase.preconditions,
      test_steps: testCase.test_steps,
      expected_result: testCase.expected_result,
    });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this test case?')) return;
    
    try {
      await testCasesApi.delete(id);
      showToast('Test case deleted successfully', 'success');
      await loadTestCases(page);
    } catch (error) {
      console.error('Error deleting test case:', error);
      showToast('Failed to delete test case', 'error');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      type: TestCaseType.FUNCTIONAL,
      priority: PriorityLevel.MEDIUM,
      status: TestCaseStatus.DRAFT,
      automated: false,
    });
  };

  const handleCancel = () => {
    setShowModal(false);
    setEditingId(null);
    resetForm();
  };

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
        <h1 className="text-3xl font-bold text-gray-900">
          Test Cases {total > 0 && <span className="text-lg font-normal text-gray-500">({total} total)</span>}
        </h1>
        {isAdmin && (
          <button
            onClick={() => setShowModal(true)}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            + New Test Case
          </button>
        )}
      </div>

      {testCases.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <p className="text-gray-600 text-lg">No test cases yet</p>
          <p className="text-gray-500 text-sm mt-2">
            Click "New Test Case" to create your first test case
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {testCases.map((tc) => (
            <div key={tc.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">{tc.title}</h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      tc.priority === 'critical' ? 'bg-red-100 text-red-800' :
                      tc.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                      tc.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {tc.priority}
                    </span>
                    <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded">
                      {tc.type}
                    </span>
                    <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded">
                      {tc.status}
                    </span>
                    {tc.automated && (
                      <span className="px-2 py-1 text-xs font-medium bg-indigo-100 text-indigo-800 rounded">
                        Automated
                      </span>
                    )}
                  </div>
                  <p className="text-gray-600 mb-3">{tc.description}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    {tc.external_id && <span>ID: {tc.external_id}</span>}
                    {tc.module && <span>Module: {tc.module}</span>}
                    <span>Version: {tc.version}</span>
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  {isAdmin && (
                    <>
                      <button
                        onClick={() => handleEdit(tc)}
                        className="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(tc.id)}
                        className="px-4 py-2 text-sm bg-red-500 text-white rounded hover:bg-red-600"
                      >
                        Delete
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Pagination page={page} pages={pages} total={total} onPageChange={setPage} />

      {showModal && isAdmin && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">
              {editingId ? 'Edit Test Case' : 'New Test Case'}
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description *
                  </label>
                  <textarea
                    required
                    rows={3}
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Type *</label>
                    <select
                      value={formData.type}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value as TestCaseType })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="FUNCTIONAL">Functional</option>
                      <option value="INTEGRATION">Integration</option>
                      <option value="SYSTEM">System</option>
                      <option value="ACCEPTANCE">Acceptance</option>
                      <option value="REGRESSION">Regression</option>
                      <option value="SMOKE">Smoke</option>
                      <option value="PERFORMANCE">Performance</option>
                      <option value="SECURITY">Security</option>
                      <option value="USABILITY">Usability</option>
                      <option value="API">API</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Priority *</label>
                    <select
                      value={formData.priority}
                      onChange={(e) => setFormData({ ...formData, priority: e.target.value as PriorityLevel })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="CRITICAL">Critical</option>
                      <option value="HIGH">High</option>
                      <option value="MEDIUM">Medium</option>
                      <option value="LOW">Low</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Status *</label>
                    <select
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value as TestCaseStatus })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="DRAFT">Draft</option>
                      <option value="READY">Ready</option>
                      <option value="IN_PROGRESS">In Progress</option>
                      <option value="PASSED">Passed</option>
                      <option value="FAILED">Failed</option>
                      <option value="BLOCKED">Blocked</option>
                      <option value="SKIPPED">Skipped</option>
                      <option value="DEPRECATED">Deprecated</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Preconditions
                  </label>
                  <textarea
                    rows={2}
                    value={formData.preconditions || ''}
                    onChange={(e) => setFormData({ ...formData, preconditions: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Test Steps
                  </label>
                  <textarea
                    rows={3}
                    value={formData.test_steps || ''}
                    onChange={(e) => setFormData({ ...formData, test_steps: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Expected Result
                  </label>
                  <textarea
                    rows={2}
                    value={formData.expected_result || ''}
                    onChange={(e) => setFormData({ ...formData, expected_result: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.automated}
                      onChange={(e) => setFormData({ ...formData, automated: e.target.checked })}
                      className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Automated Test</span>
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Module</label>
                  <input
                    type="text"
                    value={formData.module || ''}
                    onChange={(e) => setFormData({ ...formData, module: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
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
                  {editingId ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
