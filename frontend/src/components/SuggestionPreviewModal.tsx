import React from 'react';
import { SuggestionStatus } from '../types/api';
import type { Suggestion, Requirement, TestCase } from '../types/api';

interface SuggestionPreviewModalProps {
  suggestion: Suggestion;
  requirement: Requirement | undefined;
  testCase: TestCase | undefined;
  readOnly?: boolean;
  onClose: () => void;
  onReview: (id: string, status: SuggestionStatus) => void;
}

export const SuggestionPreviewModal: React.FC<SuggestionPreviewModalProps> = ({
  suggestion,
  requirement,
  testCase,
  readOnly = false,
  onClose,
  onReview,
}) => {
  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 p-6 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Suggestion Preview</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">
            ✕
          </button>
        </div>

        {/* Full details of requirement and test case */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Requirement full view */}
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-bold mb-3 text-blue-800">Requirement Details</h3>
            <div className="mb-3">
              <span className="text-sm font-semibold text-gray-700">Title:</span>
              <p className="text-gray-900">{requirement?.title || 'Unknown'}</p>
            </div>
            <div className="mb-3">
              <span className="text-sm font-semibold text-gray-700">Description:</span>
              <p className="text-gray-900 whitespace-pre-wrap">
                {requirement?.description || 'No description'}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="font-semibold text-gray-700">ID:</span>
                <p className="text-gray-900">{requirement?.external_id || 'N/A'}</p>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Priority:</span>
                <p className="text-gray-900">{requirement?.priority || 'N/A'}</p>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Type:</span>
                <p className="text-gray-900">{requirement?.type || 'N/A'}</p>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Status:</span>
                <p className="text-gray-900">{requirement?.status || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Test case full view */}
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-bold mb-3 text-green-800">Test Case Details</h3>
            <div className="mb-3">
              <span className="text-sm font-semibold text-gray-700">Title:</span>
              <p className="text-gray-900">{testCase?.title || 'Unknown'}</p>
            </div>
            <div className="mb-3">
              <span className="text-sm font-semibold text-gray-700">Description:</span>
              <p className="text-gray-900 whitespace-pre-wrap">
                {testCase?.description || 'No description'}
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span className="font-semibold text-gray-700">ID:</span>
                <p className="text-gray-900">{testCase?.external_id || 'N/A'}</p>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Priority:</span>
                <p className="text-gray-900">{testCase?.priority || 'N/A'}</p>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Type:</span>
                <p className="text-gray-900">{testCase?.type || 'N/A'}</p>
              </div>
              <div>
                <span className="font-semibold text-gray-700">Status:</span>
                <p className="text-gray-900">{testCase?.status || 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Suggestion metadata */}
        <div className="border rounded-lg p-4 mb-6 bg-purple-50">
          <h3 className="text-lg font-bold mb-3 text-purple-800">Suggestion Details</h3>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-semibold text-gray-700">Similarity Score:</span>
              <p className="text-2xl font-bold text-purple-700">
                {(suggestion.similarity_score * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <span className="font-semibold text-gray-700">Algorithm:</span>
              <p className="text-gray-900">{suggestion.suggestion_method}</p>
            </div>
            <div>
              <span className="font-semibold text-gray-700">Created:</span>
              <p className="text-gray-900">
                {new Date(suggestion.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
          {suggestion.suggestion_reason && (
            <div className="mt-3">
              <span className="font-semibold text-gray-700">Reason:</span>
              <p className="text-gray-900">{suggestion.suggestion_reason}</p>
            </div>
          )}
        </div>

        <div className="flex gap-3 justify-end">
          {!readOnly && (
            <>
              <button
                onClick={() => {
                  onReview(suggestion.id, SuggestionStatus.REJECTED);
                  onClose();
                }}
                className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
              >
                Reject
              </button>
              <button
                onClick={() => {
                  onReview(suggestion.id, SuggestionStatus.ACCEPTED);
                  onClose();
                }}
                className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
              >
                Accept
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
