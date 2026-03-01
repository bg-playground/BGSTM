import React, { useCallback, useEffect, useState } from 'react';
import { requirementsApi } from '../api/requirements';
import { RequirementType, PriorityLevel, RequirementStatus } from '../types/api';
import type { Requirement, RequirementCreate, RequirementUpdate } from '../types/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { Pagination } from '../components/Pagination';
import { useToast } from '../context/ToastContext';
import { useRoleGate } from '../hooks/useRoleGate';

export const RequirementsPage: React.FC = () => {
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(0);
  const PAGE_SIZE = 50;
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState<RequirementCreate>({
    title: '',
    description: '',
    type: RequirementType.FUNCTIONAL,
    priority: PriorityLevel.MEDIUM,
    status: RequirementStatus.DRAFT,
  });
  const { showToast } = useToast();
  const { isAdmin } = useRoleGate();

  const loadRequirements = useCallback(async (targetPage = page) => {
    try {
      setLoading(true);
      const data = await requirementsApi.list(targetPage, PAGE_SIZE);
      setRequirements(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (error) {
      console.error('Error loading requirements:', error);
      showToast('Failed to load requirements', 'error');
    } finally {
      setLoading(false);
    }
  }, [page, showToast]);

  useEffect(() => {
    loadRequirements(page);
  }, [page, loadRequirements]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await requirementsApi.update(editingId, formData as RequirementUpdate);
        showToast('Requirement updated successfully', 'success');
      } else {
        await requirementsApi.create(formData);
        showToast('Requirement created successfully', 'success');
      }
      setShowModal(false);
      setEditingId(null);
      resetForm();
      await loadRequirements(page);
    } catch (error) {
      console.error('Error saving requirement:', error);
      showToast('Failed to save requirement', 'error');
    }
  };

  const handleEdit = (requirement: Requirement) => {
    setEditingId(requirement.id);
    setFormData({
      title: requirement.title,
      description: requirement.description,
      type: requirement.type,
      priority: requirement.priority,
      status: requirement.status,
      module: requirement.module,
      tags: requirement.tags,
    });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this requirement?')) return;
    
    try {
      await requirementsApi.delete(id);
      showToast('Requirement deleted successfully', 'success');
      await loadRequirements(page);
    } catch (error) {
      console.error('Error deleting requirement:', error);
      showToast('Failed to delete requirement', 'error');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      type: RequirementType.FUNCTIONAL,
      priority: PriorityLevel.MEDIUM,
      status: RequirementStatus.DRAFT,
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
          Requirements {total > 0 && <span className="text-lg font-normal text-gray-500">({total} total)</span>}
        </h1>
        {isAdmin && (
          <button
            onClick={() => setShowModal(true)}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            + New Requirement
          </button>
        )}
      </div>

      {requirements.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <p className="text-gray-600 text-lg">No requirements yet</p>
          <p className="text-gray-500 text-sm mt-2">
            Click "New Requirement" to create your first requirement
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {requirements.map((req) => (
            <div key={req.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">{req.title}</h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${
                      req.priority === 'critical' ? 'bg-red-100 text-red-800' :
                      req.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                      req.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {req.priority}
                    </span>
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                      {req.type}
                    </span>
                    <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded">
                      {req.status}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-3">{req.description}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    {req.external_id && <span>ID: {req.external_id}</span>}
                    {req.module && <span>Module: {req.module}</span>}
                    <span>Version: {req.version}</span>
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  {isAdmin && (
                    <>
                      <button
                        onClick={() => handleEdit(req)}
                        className="px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(req.id)}
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
              {editingId ? 'Edit Requirement' : 'New Requirement'}
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label htmlFor="req-title" className="block text-sm font-medium text-gray-700 mb-1">
                    Title *
                  </label>
                  <input
                    id="req-title"
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                <div>
                  <label htmlFor="req-description" className="block text-sm font-medium text-gray-700 mb-1">
                    Description *
                  </label>
                  <textarea
                    id="req-description"
                    required
                    rows={4}
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label htmlFor="req-type" className="block text-sm font-medium text-gray-700 mb-1">Type *</label>
                    <select
                      id="req-type"
                      value={formData.type}
                      onChange={(e) => setFormData({ ...formData, type: e.target.value as RequirementType })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value={RequirementType.FUNCTIONAL}>Functional</option>
                      <option value={RequirementType.NON_FUNCTIONAL}>Non-Functional</option>
                      <option value={RequirementType.TECHNICAL}>Technical</option>
                      <option value={RequirementType.BUSINESS}>Business</option>
                      <option value={RequirementType.SECURITY}>Security</option>
                      <option value={RequirementType.PERFORMANCE}>Performance</option>
                      <option value={RequirementType.USABILITY}>Usability</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="req-priority" className="block text-sm font-medium text-gray-700 mb-1">Priority *</label>
                    <select
                      id="req-priority"
                      value={formData.priority}
                      onChange={(e) => setFormData({ ...formData, priority: e.target.value as PriorityLevel })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value={PriorityLevel.CRITICAL}>Critical</option>
                      <option value={PriorityLevel.HIGH}>High</option>
                      <option value={PriorityLevel.MEDIUM}>Medium</option>
                      <option value={PriorityLevel.LOW}>Low</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="req-status" className="block text-sm font-medium text-gray-700 mb-1">Status *</label>
                    <select
                      id="req-status"
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value as RequirementStatus })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value={RequirementStatus.DRAFT}>Draft</option>
                      <option value={RequirementStatus.APPROVED}>Approved</option>
                      <option value={RequirementStatus.IN_PROGRESS}>In Progress</option>
                      <option value={RequirementStatus.COMPLETED}>Completed</option>
                      <option value={RequirementStatus.DEPRECATED}>Deprecated</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label htmlFor="req-module" className="block text-sm font-medium text-gray-700 mb-1">Module</label>
                  <input
                    id="req-module"
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
