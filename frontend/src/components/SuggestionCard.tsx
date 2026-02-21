import React from 'react';
import { SuggestionStatus } from '../types/api';
import type { Suggestion, Requirement, TestCase } from '../types/api';

interface SuggestionCardProps {
  suggestion: Suggestion;
  requirement: Requirement | undefined;
  testCase: TestCase | undefined;
  isSelected: boolean;
  onToggleSelect: (id: string, checked: boolean) => void;
  onReview: (id: string, status: SuggestionStatus) => void;
  onPreview: (suggestion: Suggestion) => void;
}

export const SuggestionCard: React.FC<SuggestionCardProps> = ({
  suggestion,
  requirement,
  testCase,
  isSelected,
  onToggleSelect,
  onReview,
  onPreview,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={(e) => onToggleSelect(suggestion.id, e.target.checked)}
          className="mt-1"
        />
        <div className="flex-1">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border-r pr-6">
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-sm font-semibold text-gray-500 uppercase">Requirement</h3>
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
                onClick={() => onPreview(suggestion)}
                className="text-sm text-primary-600 hover:underline"
              >
                Quick Preview
              </button>
              <button
                onClick={() => onReview(suggestion.id, SuggestionStatus.REJECTED)}
                className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                Reject
              </button>
              <button
                onClick={() => onReview(suggestion.id, SuggestionStatus.ACCEPTED)}
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
};
