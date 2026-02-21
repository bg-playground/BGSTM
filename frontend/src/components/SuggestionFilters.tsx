import React, { useCallback, useEffect, useRef, useState } from 'react';

export const DEFAULT_FILTERS = {
  minScore: 0,
  maxScore: 1,
  algorithm: 'all',
  sortBy: 'score',
  sortOrder: 'desc',
  search: '',
};

export type Filters = typeof DEFAULT_FILTERS;

interface SuggestionFiltersProps {
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
  onReset?: () => void;
}

export const SuggestionFilters: React.FC<SuggestionFiltersProps> = ({ filters, onFiltersChange, onReset }) => {
  const [searchInput, setSearchInput] = useState(filters.search);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Clear debounce timer on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  // Sync searchInput when filters.search is reset externally (e.g. Reset button)
  useEffect(() => {
    setSearchInput(filters.search);
  }, [filters.search]);

  const handleSearchChange = useCallback(
    (value: string) => {
      setSearchInput(value);
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        onFiltersChange({ ...filters, search: value });
      }, 300);
    },
    [filters, onFiltersChange]
  );

  const handleReset = useCallback(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (onReset) {
      onReset();
    } else {
      onFiltersChange(DEFAULT_FILTERS);
    }
  }, [onReset, onFiltersChange]);

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      {/* Search input - full width at top */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
        <input
          type="text"
          value={searchInput}
          onChange={(e) => handleSearchChange(e.target.value)}
          placeholder="Search requirements or test cases..."
          className="w-full border rounded px-3 py-2"
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {/* Min Score */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Min Score</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={filters.minScore}
            onChange={(e) => onFiltersChange({ ...filters, minScore: parseFloat(e.target.value) })}
            className="w-full"
          />
          <span className="text-xs text-gray-600">{(filters.minScore * 100).toFixed(0)}%</span>
        </div>

        {/* Algorithm Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Algorithm</label>
          <select
            value={filters.algorithm}
            onChange={(e) => onFiltersChange({ ...filters, algorithm: e.target.value })}
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
          <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
          <select
            value={filters.sortBy}
            onChange={(e) => onFiltersChange({ ...filters, sortBy: e.target.value })}
            className="w-full border rounded px-3 py-2"
          >
            <option value="score">Similarity Score</option>
            <option value="date">Date Created</option>
            <option value="algorithm">Algorithm</option>
          </select>
        </div>

        {/* Sort Order */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Order</label>
          <select
            value={filters.sortOrder}
            onChange={(e) => onFiltersChange({ ...filters, sortOrder: e.target.value })}
            className="w-full border rounded px-3 py-2"
          >
            <option value="desc">High to Low</option>
            <option value="asc">Low to High</option>
          </select>
        </div>

        {/* Reset Filters */}
        <div className="flex items-end">
          <button
            onClick={handleReset}
            className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          >
            Reset
          </button>
        </div>
      </div>
    </div>
  );
};
