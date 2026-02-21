import React from 'react';
import type { Suggestion } from '../types/api';

interface SuggestionStatsProps {
  suggestions: Suggestion[];
}

export const SuggestionStats: React.FC<SuggestionStatsProps> = ({ suggestions }) => {
  if (suggestions.length === 0) {
    return null;
  }

  const avgScore = suggestions.reduce((sum, s) => sum + s.similarity_score, 0) / suggestions.length;

  const algorithmCounts = suggestions.reduce<Record<string, number>>((acc, s) => {
    acc[s.suggestion_method] = (acc[s.suggestion_method] ?? 0) + 1;
    return acc;
  }, {});

  const algorithmBreakdown = Object.entries(algorithmCounts)
    .map(([method, count]) => `${method}: ${count}`)
    .join(', ');

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6 flex flex-wrap gap-6 text-sm">
      <div>
        <span className="font-medium text-gray-700">Pending:</span>{' '}
        <span className="font-semibold text-gray-900">{suggestions.length}</span>
      </div>
      <div>
        <span className="font-medium text-gray-700">Avg Score:</span>{' '}
        <span className="font-semibold text-purple-700">{(avgScore * 100).toFixed(1)}%</span>
      </div>
      <div>
        <span className="font-medium text-gray-700">By Algorithm:</span>{' '}
        <span className="text-gray-900">{algorithmBreakdown}</span>
      </div>
    </div>
  );
};
