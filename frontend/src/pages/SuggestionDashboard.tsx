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
  const { showToast } = useToast();

  const loadData = async () => {
    try {
      setLoading(true);
      const [suggestionData, reqData, tcData] = await Promise.all([
        suggestionsApi.listPending(),
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
  }, []);

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
            );
          })}
        </div>
      )}
    </div>
  );
};
