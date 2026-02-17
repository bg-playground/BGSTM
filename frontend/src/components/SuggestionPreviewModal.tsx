import React, { useEffect } from 'react';
import type { Suggestion, Requirement, TestCase } from '../types/api';

interface SuggestionPreviewModalProps {
  isOpen: boolean;
  suggestion: Suggestion | null;
  requirement?: Requirement;
  testCase?: TestCase;
  onClose: () => void;
  onAccept: (id: string) => void;
  onReject: (id: string) => void;
}

export const SuggestionPreviewModal: React.FC<SuggestionPreviewModalProps> = ({
  isOpen,
  suggestion,
  requirement,
  testCase,
  onClose,
  onAccept,
  onReject,
}) => {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !suggestion) return null;

  const confidencePercent = Math.round(suggestion.similarity_score * 100);

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" onClick={onClose}>
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" />

        {/* Modal panel */}
        <div
          className="inline-block w-full max-w-6xl my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
            <div className="flex items-center gap-4">
              <h2 className="text-2xl font-bold text-gray-900">Suggestion Details</h2>
              <span
                className={`px-3 py-1 text-sm font-semibold rounded ${
                  confidencePercent >= 80
                    ? 'bg-green-100 text-green-800'
                    : confidencePercent >= 60
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-orange-100 text-orange-800'
                }`}
              >
                {confidencePercent}% Confidence
              </span>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Close modal"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-6 max-h-[70vh] overflow-y-auto">
            {/* Metadata */}
            <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-500">Algorithm</p>
                <p className="text-base font-semibold text-gray-900">
                  {suggestion.suggestion_method.replace(/_/g, ' ').toUpperCase()}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Created</p>
                <p className="text-base font-semibold text-gray-900">
                  {new Date(suggestion.created_at).toLocaleString()}
                </p>
              </div>
              {suggestion.suggestion_reason && (
                <div className="col-span-2">
                  <p className="text-sm font-medium text-gray-500">Reason</p>
                  <p className="text-base text-gray-900">{suggestion.suggestion_reason}</p>
                </div>
              )}
            </div>

            {/* Side-by-side comparison */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Requirement Details */}
              <div className="border rounded-lg p-6 bg-blue-50">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <span className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    R
                  </span>
                  Requirement
                </h3>

                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Title</p>
                    <p className="text-lg font-semibold text-gray-900">{requirement?.title || 'N/A'}</p>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-600">Description</p>
                    <p className="text-base text-gray-900 whitespace-pre-wrap">
                      {requirement?.description || 'N/A'}
                    </p>
                  </div>

                  {requirement?.priority && (
                    <div>
                      <p className="text-sm font-medium text-gray-600">Priority</p>
                      <span className="inline-block px-3 py-1 text-sm font-medium bg-blue-100 text-blue-800 rounded">
                        {requirement.priority}
                      </span>
                    </div>
                  )}

                  {requirement?.type && (
                    <div>
                      <p className="text-sm font-medium text-gray-600">Type</p>
                      <p className="text-base text-gray-900">{requirement.type}</p>
                    </div>
                  )}

                  {requirement?.module && (
                    <div>
                      <p className="text-sm font-medium text-gray-600">Module</p>
                      <p className="text-base text-gray-900">{requirement.module}</p>
                    </div>
                  )}

                  {requirement?.tags && requirement.tags.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-2">Tags</p>
                      <div className="flex flex-wrap gap-2">
                        {requirement.tags.map((tag, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Test Case Details */}
              <div className="border rounded-lg p-6 bg-green-50">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <span className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    T
                  </span>
                  Test Case
                </h3>

                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Title</p>
                    <p className="text-lg font-semibold text-gray-900">{testCase?.title || 'N/A'}</p>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-600">Description</p>
                    <p className="text-base text-gray-900 whitespace-pre-wrap">
                      {testCase?.description || 'N/A'}
                    </p>
                  </div>

                  {testCase?.preconditions && (
                    <div>
                      <p className="text-sm font-medium text-gray-600">Preconditions</p>
                      <p className="text-base text-gray-900 whitespace-pre-wrap">
                        {testCase.preconditions}
                      </p>
                    </div>
                  )}

                  {testCase?.test_steps && (
                    <div>
                      <p className="text-sm font-medium text-gray-600">Test Steps</p>
                      <p className="text-base text-gray-900 whitespace-pre-wrap">{testCase.test_steps}</p>
                    </div>
                  )}

                  {testCase?.expected_result && (
                    <div>
                      <p className="text-sm font-medium text-gray-600">Expected Result</p>
                      <p className="text-base text-gray-900 whitespace-pre-wrap">
                        {testCase.expected_result}
                      </p>
                    </div>
                  )}

                  {testCase?.priority && (
                    <div>
                      <p className="text-sm font-medium text-gray-600">Priority</p>
                      <span className="inline-block px-3 py-1 text-sm font-medium bg-green-100 text-green-800 rounded">
                        {testCase.priority}
                      </span>
                    </div>
                  )}

                  {testCase?.module && (
                    <div>
                      <p className="text-sm font-medium text-gray-600">Module</p>
                      <p className="text-base text-gray-900">{testCase.module}</p>
                    </div>
                  )}

                  {testCase?.tags && testCase.tags.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-2">Tags</p>
                      <div className="flex flex-wrap gap-2">
                        {testCase.tags.map((tag, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-3 px-6 py-4 border-t bg-gray-50">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors font-medium"
            >
              Skip (Esc)
            </button>
            <button
              onClick={() => {
                onReject(suggestion.id);
                onClose();
              }}
              className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium"
            >
              Reject (R)
            </button>
            <button
              onClick={() => {
                onAccept(suggestion.id);
                onClose();
              }}
              className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium"
            >
              Accept (A)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
