import React from 'react';
import type { Suggestion, Requirement, TestCase, SuggestionStatus } from '../types/api';

interface SuggestionCardProps {
  suggestion: Suggestion;
  requirement?: Requirement;
  testCase?: TestCase;
  isSelected: boolean;
  isFocused: boolean;
  onSelect: (id: string) => void;
  onAccept: (id: string) => void;
  onReject: (id: string) => void;
  onClick: (id: string) => void;
}

const getConfidenceColor = (score: number): string => {
  if (score >= 0.8) return 'bg-green-100 text-green-800 border-green-300';
  if (score >= 0.6) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
  return 'bg-orange-100 text-orange-800 border-orange-300';
};

const getConfidenceBarColor = (score: number): string => {
  if (score >= 0.8) return 'bg-green-500';
  if (score >= 0.6) return 'bg-yellow-500';
  return 'bg-orange-500';
};

const getAlgorithmBadgeColor = (method: string): string => {
  const colors: Record<string, string> = {
    llm_embedding: 'bg-purple-100 text-purple-800',
    hybrid: 'bg-blue-100 text-blue-800',
    semantic_similarity: 'bg-indigo-100 text-indigo-800',
    keyword_match: 'bg-teal-100 text-teal-800',
    heuristic: 'bg-gray-100 text-gray-800',
  };
  return colors[method] || 'bg-gray-100 text-gray-800';
};

const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  return date.toLocaleDateString();
};

export const SuggestionCard: React.FC<SuggestionCardProps> = ({
  suggestion,
  requirement,
  testCase,
  isSelected,
  isFocused,
  onSelect,
  onAccept,
  onReject,
  onClick,
}) => {
  const confidencePercent = Math.round(suggestion.similarity_score * 100);

  return (
    <div
      className={`bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer ${
        isFocused ? 'ring-2 ring-primary-500 ring-offset-2' : ''
      } ${isSelected ? 'border-2 border-primary-500' : 'border border-transparent'}`}
      onClick={() => onClick(suggestion.id)}
    >
      {/* Header with checkbox and metadata */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={(e) => {
              e.stopPropagation();
              onSelect(suggestion.id);
            }}
            onClick={(e) => e.stopPropagation()}
            className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500 cursor-pointer"
          />
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className={`px-2 py-1 text-xs font-medium rounded ${getAlgorithmBadgeColor(
                suggestion.suggestion_method
              )}`}
            >
              {suggestion.suggestion_method.replace(/_/g, ' ').toUpperCase()}
            </span>
            <span className="text-xs text-gray-500">{formatTimeAgo(suggestion.created_at)}</span>
          </div>
        </div>

        {/* Confidence Badge */}
        <div
          className={`px-3 py-1 text-sm font-semibold rounded border ${getConfidenceColor(
            suggestion.similarity_score
          )}`}
        >
          {confidencePercent}%
        </div>
      </div>

      {/* Confidence Bar */}
      <div className="mb-4">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${getConfidenceBarColor(
              suggestion.similarity_score
            )}`}
            style={{ width: `${confidencePercent}%` }}
          />
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Requirement */}
        <div className="border-r pr-6">
          <div className="flex items-start justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-500 uppercase">Requirement</h3>
            {requirement?.priority && (
              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                {requirement.priority}
              </span>
            )}
          </div>
          <h4 className="text-lg font-semibold text-gray-900 mb-2">
            {requirement?.title || 'Unknown'}
          </h4>
          <p className="text-sm text-gray-600 line-clamp-3">{requirement?.description || 'No description'}</p>
          {requirement?.tags && requirement.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {requirement.tags.slice(0, 3).map((tag, idx) => (
                <span key={idx} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                  {tag}
                </span>
              ))}
              {requirement.tags.length > 3 && (
                <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                  +{requirement.tags.length - 3}
                </span>
              )}
            </div>
          )}
          {requirement?.module && (
            <p className="text-xs text-gray-500 mt-2">Module: {requirement.module}</p>
          )}
        </div>

        {/* Test Case */}
        <div className="pl-6">
          <div className="flex items-start justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-500 uppercase">Test Case</h3>
            {testCase?.priority && (
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
                {testCase.priority}
              </span>
            )}
          </div>
          <h4 className="text-lg font-semibold text-gray-900 mb-2">{testCase?.title || 'Unknown'}</h4>
          <p className="text-sm text-gray-600 line-clamp-3">{testCase?.description || 'No description'}</p>
          {testCase?.tags && testCase.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {testCase.tags.slice(0, 3).map((tag, idx) => (
                <span key={idx} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                  {tag}
                </span>
              ))}
              {testCase.tags.length > 3 && (
                <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                  +{testCase.tags.length - 3}
                </span>
              )}
            </div>
          )}
          {testCase?.module && <p className="text-xs text-gray-500 mt-2">Module: {testCase.module}</p>}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mt-6 pt-6 border-t flex items-center justify-end gap-3">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onReject(suggestion.id);
          }}
          className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium"
        >
          Reject
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onAccept(suggestion.id);
          }}
          className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium"
        >
          Accept
        </button>
      </div>
    </div>
  );
};
