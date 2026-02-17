import React from 'react';
import type { Suggestion } from '../types/api';

interface SuggestionStatsProps {
  suggestions: Suggestion[];
}

export const SuggestionStats: React.FC<SuggestionStatsProps> = ({ suggestions }) => {
  const totalPending = suggestions.length;
  const avgConfidence =
    suggestions.length > 0
      ? suggestions.reduce((sum, s) => sum + s.similarity_score, 0) / suggestions.length
      : 0;

  // Group by algorithm
  const algorithmCounts = suggestions.reduce(
    (acc, s) => {
      acc[s.suggestion_method] = (acc[s.suggestion_method] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      {/* Total Pending */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">Pending Suggestions</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{totalPending}</p>
          </div>
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg
              className="w-6 h-6 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Average Confidence */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">Avg. Confidence</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">
              {Math.round(avgConfidence * 100)}%
            </p>
          </div>
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <svg
              className="w-6 h-6 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Algorithm Breakdown */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-medium text-gray-600">By Algorithm</p>
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <svg
              className="w-6 h-6 text-purple-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
              />
            </svg>
          </div>
        </div>
        <div className="space-y-2">
          {Object.entries(algorithmCounts)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 3)
            .map(([algorithm, count]) => (
              <div key={algorithm} className="flex justify-between items-center text-sm">
                <span className="text-gray-600 truncate">
                  {algorithm.replace(/_/g, ' ').substring(0, 15)}
                </span>
                <span className="font-semibold text-gray-900">{count}</span>
              </div>
            ))}
          {Object.keys(algorithmCounts).length === 0 && (
            <p className="text-sm text-gray-500 italic">No data</p>
          )}
        </div>
      </div>
    </div>
  );
};
