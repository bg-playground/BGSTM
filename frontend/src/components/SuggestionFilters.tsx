import React from 'react';
import { SuggestionMethod, type SuggestionFilters as FilterType } from '../types/api';

interface SuggestionFiltersProps {
  filters: FilterType;
  onFiltersChange: (filters: FilterType) => void;
  onClearFilters: () => void;
}

export const SuggestionFilters: React.FC<SuggestionFiltersProps> = ({
  filters,
  onFiltersChange,
  onClearFilters,
}) => {
  const updateFilter = (key: keyof FilterType, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const hasActiveFilters = () => {
    return (
      filters.min_score !== undefined ||
      filters.max_score !== undefined ||
      filters.algorithm !== undefined ||
      filters.search !== undefined
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        {hasActiveFilters() && (
          <button
            onClick={onClearFilters}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Clear All
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Search */}
        <div className="lg:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            type="text"
            placeholder="Search requirements or test cases..."
            value={filters.search || ''}
            onChange={(e) => updateFilter('search', e.target.value || undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        {/* Algorithm Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Algorithm</label>
          <select
            value={filters.algorithm || ''}
            onChange={(e) => updateFilter('algorithm', e.target.value || undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">All Algorithms</option>
            <option value={SuggestionMethod.LLM_EMBEDDING}>LLM Embedding</option>
            <option value={SuggestionMethod.HYBRID}>Hybrid</option>
            <option value={SuggestionMethod.SEMANTIC_SIMILARITY}>Semantic Similarity</option>
            <option value={SuggestionMethod.KEYWORD_MATCH}>Keyword Match</option>
            <option value={SuggestionMethod.HEURISTIC}>Heuristic</option>
          </select>
        </div>

        {/* Sort By */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
          <select
            value={filters.sort_by || 'similarity_score'}
            onChange={(e) =>
              updateFilter('sort_by', e.target.value as 'similarity_score' | 'created_at')
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="similarity_score">Confidence Score</option>
            <option value="created_at">Date Created</option>
          </select>
        </div>

        {/* Confidence Score Range */}
        <div className="lg:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Confidence Score: {filters.min_score !== undefined ? Math.round(filters.min_score * 100) : 0}
            % - {filters.max_score !== undefined ? Math.round(filters.max_score * 100) : 100}%
          </label>
          <div className="flex gap-2 items-center">
            <input
              type="range"
              min="0"
              max="100"
              value={filters.min_score !== undefined ? filters.min_score * 100 : 0}
              onChange={(e) => updateFilter('min_score', Number(e.target.value) / 100)}
              className="flex-1"
            />
            <input
              type="range"
              min="0"
              max="100"
              value={filters.max_score !== undefined ? filters.max_score * 100 : 100}
              onChange={(e) => updateFilter('max_score', Number(e.target.value) / 100)}
              className="flex-1"
            />
          </div>
        </div>

        {/* Sort Order */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Order</label>
          <select
            value={filters.sort_order || 'desc'}
            onChange={(e) => updateFilter('sort_order', e.target.value as 'asc' | 'desc')}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="desc">High to Low</option>
            <option value="asc">Low to High</option>
          </select>
        </div>
      </div>
    </div>
  );
};
