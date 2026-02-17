import React, { useEffect, useState } from 'react';
import { suggestionsApi } from '../api/suggestions';
import { requirementsApi } from '../api/requirements';
import { testCasesApi } from '../api/testCases';
import { SuggestionStatus } from '../types/api';
import type { Suggestion, Requirement, TestCase } from '../types/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useToast } from '../components/Toast';

export const SuggestionDashboard: React.FC = () => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [requirements, setRequirements] = useState<Map<string, Requirement>>(new Map());
  const [testCases, setTestCases] = useState<Map<string, TestCase>>(new Map());
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [previewSuggestion, setPreviewSuggestion] = useState<Suggestion | null>(null);
  const { showToast } = useToast();

  // Filters state
  const [filters, setFilters] = useState({
    minScore: 0,
    maxScore: 1,
    algorithm: 'all',
    sortBy: 'score',
    sortOrder: 'desc'
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [suggestionData, reqData, tcData] = await Promise.all([
        suggestionsApi.listPending({
          minScore: filters.minScore,
          maxScore: filters.maxScore,
          algorithm: filters.algorithm === 'all' ? undefined : filters.algorithm,
          sortBy: filters.sortBy,
          sortOrder: filters.sortOrder
        }),
        requirementsApi.list(),
        testCasesApi.list(),
      ]);

      setSuggestions(suggestionData);
      setRequirements(new Map(reqData.map((r) => [r.id, r])));
      setTestCases(new Map(tcData.map((tc) => [tc.id, tc])));
    } catch (error) {
      console.error('Error loading data:', error);
      showToast('Failed to load suggestions', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filters]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleReview = async (id: string, status: SuggestionStatus) => {
    try {
      await suggestionsApi.review(id, { status });
      showToast(
        `Suggestion ${status === SuggestionStatus.ACCEPTED ? 'accepted' : 'rejected'}`,
        status === SuggestionStatus.ACCEPTED ? 'success' : 'info'
      );
      // Remove from list
      setSuggestions((prev) => prev.filter((s) => s.id !== id));
    } catch (error) {
      console.error('Error reviewing suggestion:', error);
      showToast('Failed to review suggestion', 'error');
    }
  };

  const handleBulkAccept = async () => {
    try {
      await suggestionsApi.bulkReview(Array.from(selectedIds), SuggestionStatus.ACCEPTED);
      showToast(`Accepted ${selectedIds.size} suggestions`, 'success');
      setSelectedIds(new Set());
      await loadData();
    } catch {
      showToast('Failed to accept suggestions', 'error');
    }
  };

  const handleBulkReject = async () => {
    try {
      await suggestionsApi.bulkReview(Array.from(selectedIds), SuggestionStatus.REJECTED);
      showToast(`Rejected ${selectedIds.size} suggestions`, 'success');
      setSelectedIds(new Set());
      await loadData();
    } catch {
      showToast('Failed to reject suggestions', 'error');
    }
  };

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      const response = await suggestionsApi.generate();
      showToast(
        `Generated ${response.results.suggestions_created} new suggestions`,
        'success'
      );
      await loadData();
    } catch (error) {
      console.error('Error generating suggestions:', error);
      showToast('Failed to generate suggestions', 'error');
    } finally {
      setGenerating(false);
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Only if not in an input field
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch(e.key) {
        case 'a':
          // Select all visible
          setSelectedIds(new Set(suggestions.map(s => s.id)));
          break;
        case 'c':
          // Clear selection
          setSelectedIds(new Set());
          break;
        case 'Enter':
          // Accept selected
          if (selectedIds.size > 0) {
            handleBulkAccept();
          }
          break;
        case 'Delete':
        case 'Backspace':
          // Reject selected
          if (selectedIds.size > 0 && e.shiftKey) {
            e.preventDefault();
            handleBulkReject();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [suggestions, selectedIds]); // eslint-disable-line react-hooks/exhaustive-deps

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
        <h1 className="text-3xl font-bold text-gray-900">AI Suggestion Dashboard</h1>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {generating ? (
            <>
              <LoadingSpinner size="sm" />
              Generating...
            </>
          ) : (
            'Generate Suggestions'
          )}
        </button>
      </div>

      {/* Keyboard shortcuts legend */}
      <div className="text-sm text-gray-600 mb-4 bg-gray-50 p-3 rounded">
        <strong>Keyboard Shortcuts:</strong> 
        <kbd className="ml-2 px-2 py-1 bg-white border rounded">A</kbd> Select All • 
        <kbd className="ml-2 px-2 py-1 bg-white border rounded">C</kbd> Clear • 
        <kbd className="ml-2 px-2 py-1 bg-white border rounded">Enter</kbd> Accept • 
        <kbd className="ml-2 px-2 py-1 bg-white border rounded">Shift+Delete</kbd> Reject
      </div>

      {/* Filter and Sort Controls */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {/* Min Score */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Min Score
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={filters.minScore}
              onChange={(e) => setFilters({...filters, minScore: parseFloat(e.target.value)})}
              className="w-full"
            />
            <span className="text-xs text-gray-600">{(filters.minScore * 100).toFixed(0)}%</span>
          </div>

          {/* Algorithm Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Algorithm
            </label>
            <select
              value={filters.algorithm}
              onChange={(e) => setFilters({...filters, algorithm: e.target.value})}
              className="w-full border rounded px-3 py-2"
            >
              <option value="all">All</option>
              <option value="tfidf">TF-IDF</option>
              <option value="keyword">Keyword</option>
              <option value="hybrid">Hybrid</option>
              <option value="llm">LLM</option>
            </select>
          </div>

          {/* Sort By */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sort By
            </label>
            <select
              value={filters.sortBy}
              onChange={(e) => setFilters({...filters, sortBy: e.target.value})}
              className="w-full border rounded px-3 py-2"
            >
              <option value="score">Similarity Score</option>
              <option value="date">Date Created</option>
              <option value="algorithm">Algorithm</option>
            </select>
          </div>

          {/* Sort Order */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Order
            </label>
            <select
              value={filters.sortOrder}
              onChange={(e) => setFilters({...filters, sortOrder: e.target.value})}
              className="w-full border rounded px-3 py-2"
            >
              <option value="desc">High to Low</option>
              <option value="asc">Low to High</option>
            </select>
          </div>

          {/* Reset Filters */}
          <div className="flex items-end">
            <button
              onClick={() => setFilters({minScore: 0, maxScore: 1, algorithm: 'all', sortBy: 'score', sortOrder: 'desc'})}
              className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      {suggestions.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <p className="text-gray-600 text-lg">No pending suggestions</p>
          <p className="text-gray-500 text-sm mt-2">
            Click "Generate Suggestions" to create AI-powered link recommendations
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {suggestions.map((suggestion) => {
            const requirement = requirements.get(suggestion.requirement_id);
            const testCase = testCases.get(suggestion.test_case_id);

            return (
              <div
                key={suggestion.id}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(suggestion.id)}
                    onChange={(e) => {
                      const newSelected = new Set(selectedIds);
                      if (e.target.checked) {
                        newSelected.add(suggestion.id);
                      } else {
                        newSelected.delete(suggestion.id);
                      }
                      setSelectedIds(newSelected);
                    }}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="border-r pr-6">
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="text-sm font-semibold text-gray-500 uppercase">
                            Requirement
                          </h3>
                          <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                            {requirement?.priority || 'N/A'}
                          </span>
                        </div>
                        <h4 className="text-lg font-semibold text-gray-900 mb-2">
                          {requirement?.title || 'Unknown'}
                        </h4>
                        <p className="text-sm text-gray-600 line-clamp-3">
                          {requirement?.description || 'No description'}
                        </p>
                        {requirement?.external_id && (
                          <p className="text-xs text-gray-500 mt-2">ID: {requirement.external_id}</p>
                        )}
                      </div>

                      <div className="pl-6">
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="text-sm font-semibold text-gray-500 uppercase">Test Case</h3>
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                            {testCase?.priority || 'N/A'}
                          </span>
                        </div>
                        <h4 className="text-lg font-semibold text-gray-900 mb-2">
                          {testCase?.title || 'Unknown'}
                        </h4>
                        <p className="text-sm text-gray-600 line-clamp-3">
                          {testCase?.description || 'No description'}
                        </p>
                        {testCase?.external_id && (
                          <p className="text-xs text-gray-500 mt-2">ID: {testCase.external_id}</p>
                        )}
                      </div>
                    </div>

                    <div className="mt-6 pt-6 border-t flex items-center justify-between">
                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-700">Similarity:</span>
                          <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded font-semibold">
                            {(suggestion.similarity_score * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-700">Algorithm:</span>
                          <span className="text-gray-600">{suggestion.suggestion_method}</span>
                        </div>
                      </div>

                      <div className="flex gap-3">
                        <button
                          onClick={() => setPreviewSuggestion(suggestion)}
                          className="text-sm text-primary-600 hover:underline"
                        >
                          Quick Preview
                        </button>
                        <button
                          onClick={() => handleReview(suggestion.id, SuggestionStatus.REJECTED)}
                          className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                        >
                          Reject
                        </button>
                        <button
                          onClick={() => handleReview(suggestion.id, SuggestionStatus.ACCEPTED)}
                          className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                        >
                          Accept
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Bulk action bar */}
      {selectedIds.size > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-primary-600 text-white shadow-lg p-4 flex items-center justify-between z-50">
          <div>
            <span className="font-semibold">{selectedIds.size} suggestions selected</span>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleBulkReject}
              className="px-6 py-2 bg-red-500 hover:bg-red-600 rounded-lg"
            >
              Reject Selected
            </button>
            <button
              onClick={handleBulkAccept}
              className="px-6 py-2 bg-green-500 hover:bg-green-600 rounded-lg"
            >
              Accept Selected
            </button>
            <button
              onClick={() => setSelectedIds(new Set())}
              className="px-6 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg"
            >
              Clear Selection
            </button>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {previewSuggestion && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setPreviewSuggestion(null)}>
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 p-6 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Suggestion Preview</h2>
              <button onClick={() => setPreviewSuggestion(null)} className="text-gray-500 hover:text-gray-700 text-2xl">
                ✕
              </button>
            </div>
            
            {/* Full details of requirement and test case */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Requirement full view */}
              <div className="border rounded-lg p-4">
                <h3 className="text-lg font-bold mb-3 text-blue-800">Requirement Details</h3>
                {(() => {
                  const req = requirements.get(previewSuggestion.requirement_id);
                  return (
                    <>
                      <div className="mb-3">
                        <span className="text-sm font-semibold text-gray-700">Title:</span>
                        <p className="text-gray-900">{req?.title || 'Unknown'}</p>
                      </div>
                      <div className="mb-3">
                        <span className="text-sm font-semibold text-gray-700">Description:</span>
                        <p className="text-gray-900 whitespace-pre-wrap">{req?.description || 'No description'}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <span className="font-semibold text-gray-700">ID:</span>
                          <p className="text-gray-900">{req?.external_id || 'N/A'}</p>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Priority:</span>
                          <p className="text-gray-900">{req?.priority || 'N/A'}</p>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Type:</span>
                          <p className="text-gray-900">{req?.type || 'N/A'}</p>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Status:</span>
                          <p className="text-gray-900">{req?.status || 'N/A'}</p>
                        </div>
                      </div>
                    </>
                  );
                })()}
              </div>

              {/* Test case full view */}
              <div className="border rounded-lg p-4">
                <h3 className="text-lg font-bold mb-3 text-green-800">Test Case Details</h3>
                {(() => {
                  const tc = testCases.get(previewSuggestion.test_case_id);
                  return (
                    <>
                      <div className="mb-3">
                        <span className="text-sm font-semibold text-gray-700">Title:</span>
                        <p className="text-gray-900">{tc?.title || 'Unknown'}</p>
                      </div>
                      <div className="mb-3">
                        <span className="text-sm font-semibold text-gray-700">Description:</span>
                        <p className="text-gray-900 whitespace-pre-wrap">{tc?.description || 'No description'}</p>
                      </div>
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <span className="font-semibold text-gray-700">ID:</span>
                          <p className="text-gray-900">{tc?.external_id || 'N/A'}</p>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Priority:</span>
                          <p className="text-gray-900">{tc?.priority || 'N/A'}</p>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Type:</span>
                          <p className="text-gray-900">{tc?.type || 'N/A'}</p>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Status:</span>
                          <p className="text-gray-900">{tc?.status || 'N/A'}</p>
                        </div>
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>

            {/* Suggestion metadata */}
            <div className="border rounded-lg p-4 mb-6 bg-purple-50">
              <h3 className="text-lg font-bold mb-3 text-purple-800">Suggestion Details</h3>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="font-semibold text-gray-700">Similarity Score:</span>
                  <p className="text-2xl font-bold text-purple-700">{(previewSuggestion.similarity_score * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <span className="font-semibold text-gray-700">Algorithm:</span>
                  <p className="text-gray-900">{previewSuggestion.suggestion_method}</p>
                </div>
                <div>
                  <span className="font-semibold text-gray-700">Created:</span>
                  <p className="text-gray-900">{new Date(previewSuggestion.created_at).toLocaleDateString()}</p>
                </div>
              </div>
              {previewSuggestion.suggestion_reason && (
                <div className="mt-3">
                  <span className="font-semibold text-gray-700">Reason:</span>
                  <p className="text-gray-900">{previewSuggestion.suggestion_reason}</p>
                </div>
              )}
            </div>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  handleReview(previewSuggestion.id, SuggestionStatus.REJECTED);
                  setPreviewSuggestion(null);
                }}
                className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
              >
                Reject
              </button>
              <button
                onClick={() => {
                  handleReview(previewSuggestion.id, SuggestionStatus.ACCEPTED);
                  setPreviewSuggestion(null);
                }}
                className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
              >
                Accept
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
