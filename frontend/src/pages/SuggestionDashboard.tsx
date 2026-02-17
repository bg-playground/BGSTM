import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { suggestionsApi } from '../api/suggestions';
import { requirementsApi } from '../api/requirements';
import { testCasesApi } from '../api/testCases';
import { SuggestionStatus, type SuggestionFilters as FilterType } from '../types/api';
import type { Suggestion, Requirement, TestCase } from '../types/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useToast } from '../components/Toast';
import { SuggestionCard } from '../components/SuggestionCard';
import { SuggestionFilters } from '../components/SuggestionFilters';
import { SuggestionStats } from '../components/SuggestionStats';
import { SuggestionPreviewModal } from '../components/SuggestionPreviewModal';
import { KeyboardShortcutsHelp } from '../components/KeyboardShortcutsHelp';

const STORAGE_KEY = 'suggestion-filters';

export const SuggestionDashboard: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [requirements, setRequirements] = useState<Map<string, Requirement>>(new Map());
  const [testCases, setTestCases] = useState<Map<string, TestCase>>(new Map());
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const [previewSuggestion, setPreviewSuggestion] = useState<Suggestion | null>(null);
  const [showHelp, setShowHelp] = useState(false);
  const [batchProcessing, setBatchProcessing] = useState(false);
  const { showToast } = useToast();
  const containerRef = useRef<HTMLDivElement>(null);

  // Initialize filters from localStorage or URL params
  const getInitialFilters = (): FilterType => {
    // Try URL params first
    const urlFilters: FilterType = {};
    if (searchParams.get('min_score'))
      urlFilters.min_score = parseFloat(searchParams.get('min_score')!);
    if (searchParams.get('max_score'))
      urlFilters.max_score = parseFloat(searchParams.get('max_score')!);
    if (searchParams.get('algorithm')) urlFilters.algorithm = searchParams.get('algorithm') as any;
    if (searchParams.get('search')) urlFilters.search = searchParams.get('search')!;
    if (searchParams.get('sort_by')) urlFilters.sort_by = searchParams.get('sort_by') as any;
    if (searchParams.get('sort_order')) urlFilters.sort_order = searchParams.get('sort_order') as any;

    if (Object.keys(urlFilters).length > 0) return urlFilters;

    // Fall back to localStorage
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch {
        return {};
      }
    }
    return {};
  };

  const [filters, setFilters] = useState<FilterType>(getInitialFilters);

  // Update URL and localStorage when filters change
  useEffect(() => {
    const params = new URLSearchParams();
    if (filters.min_score !== undefined) params.set('min_score', filters.min_score.toString());
    if (filters.max_score !== undefined) params.set('max_score', filters.max_score.toString());
    if (filters.algorithm) params.set('algorithm', filters.algorithm);
    if (filters.search) params.set('search', filters.search);
    if (filters.sort_by) params.set('sort_by', filters.sort_by);
    if (filters.sort_order) params.set('sort_order', filters.sort_order);

    setSearchParams(params, { replace: true });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filters));
  }, [filters, setSearchParams]);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [suggestionData, reqData, tcData] = await Promise.all([
        suggestionsApi.listPending(filters),
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
  }, [filters, showToast]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleReview = async (id: string, status: SuggestionStatus) => {
    try {
      await suggestionsApi.review(id, { status });
      showToast(
        `Suggestion ${status === SuggestionStatus.ACCEPTED ? 'accepted' : 'rejected'}`,
        status === SuggestionStatus.ACCEPTED ? 'success' : 'info'
      );
      setSuggestions((prev) => prev.filter((s) => s.id !== id));
      setSelectedIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    } catch (error) {
      console.error('Error reviewing suggestion:', error);
      showToast('Failed to review suggestion', 'error');
    }
  };

  const handleBatchReview = async (status: SuggestionStatus) => {
    if (selectedIds.size === 0) return;

    try {
      setBatchProcessing(true);
      const result = await suggestionsApi.batchReview({
        suggestion_ids: Array.from(selectedIds),
        status,
      });

      showToast(
        `Batch review complete: ${result.accepted + result.rejected} processed, ${result.failed} failed`,
        result.failed > 0 ? 'warning' : 'success'
      );

      // Refresh the list
      await loadData();
      setSelectedIds(new Set());
    } catch (error) {
      console.error('Error batch reviewing:', error);
      showToast('Failed to batch review suggestions', 'error');
    } finally {
      setBatchProcessing(false);
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

  const toggleSelection = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const selectAll = () => {
    setSelectedIds(new Set(suggestions.map((s) => s.id)));
  };

  const clearSelection = () => {
    setSelectedIds(new Set());
  };

  const handleFiltersChange = (newFilters: FilterType) => {
    setFilters(newFilters);
  };

  const handleClearFilters = () => {
    setFilters({});
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing in an input
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement ||
        e.target instanceof HTMLSelectElement
      ) {
        return;
      }

      // Ignore if modal is open (except Esc)
      if (previewSuggestion && e.key !== 'Escape') {
        return;
      }

      switch (e.key) {
        case '?':
          e.preventDefault();
          setShowHelp((prev) => !prev);
          break;
        case 'Escape':
          e.preventDefault();
          if (previewSuggestion) {
            setPreviewSuggestion(null);
          } else {
            clearSelection();
          }
          break;
        case 'ArrowUp':
          e.preventDefault();
          setFocusedIndex((prev) => Math.max(0, prev - 1));
          break;
        case 'ArrowDown':
          e.preventDefault();
          setFocusedIndex((prev) => Math.min(suggestions.length - 1, prev + 1));
          break;
        case 'Enter':
          e.preventDefault();
          if (focusedIndex >= 0 && focusedIndex < suggestions.length) {
            setPreviewSuggestion(suggestions[focusedIndex]);
          }
          break;
        case ' ':
          e.preventDefault();
          if (focusedIndex >= 0 && focusedIndex < suggestions.length) {
            toggleSelection(suggestions[focusedIndex].id);
          }
          break;
        case 'a':
        case 'A':
          if (e.shiftKey) {
            e.preventDefault();
            handleBatchReview(SuggestionStatus.ACCEPTED);
          } else if ((e.ctrlKey || e.metaKey) && !e.shiftKey) {
            e.preventDefault();
            selectAll();
          } else if (focusedIndex >= 0 && focusedIndex < suggestions.length && !e.ctrlKey && !e.metaKey) {
            e.preventDefault();
            handleReview(suggestions[focusedIndex].id, SuggestionStatus.ACCEPTED);
          }
          break;
        case 'r':
        case 'R':
          if (e.shiftKey) {
            e.preventDefault();
            handleBatchReview(SuggestionStatus.REJECTED);
          } else if (focusedIndex >= 0 && focusedIndex < suggestions.length) {
            e.preventDefault();
            handleReview(suggestions[focusedIndex].id, SuggestionStatus.REJECTED);
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [suggestions, focusedIndex, previewSuggestion, selectedIds]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const hasActiveFilters =
    filters.min_score !== undefined ||
    filters.max_score !== undefined ||
    filters.algorithm !== undefined ||
    filters.search !== undefined;

  return (
    <div className="container mx-auto px-4 py-8" ref={containerRef}>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Suggestion Dashboard</h1>
          <p className="text-gray-600 mt-1">Review and manage AI-generated requirement-test case links</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowHelp(true)}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors flex items-center gap-2"
            title="Keyboard Shortcuts"
          >
            <span className="text-lg">?</span>
            Help
          </button>
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
      </div>

      {/* Statistics */}
      <SuggestionStats suggestions={suggestions} />

      {/* Filters */}
      <SuggestionFilters
        filters={filters}
        onFiltersChange={handleFiltersChange}
        onClearFilters={handleClearFilters}
      />

      {/* Batch Actions Bar */}
      {selectedIds.size > 0 && (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="font-semibold text-primary-900">
              {selectedIds.size} suggestion{selectedIds.size !== 1 ? 's' : ''} selected
            </span>
            <button
              onClick={clearSelection}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              Clear Selection
            </button>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => handleBatchReview(SuggestionStatus.REJECTED)}
              disabled={batchProcessing}
              className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:bg-gray-400 transition-colors font-medium"
            >
              {batchProcessing ? 'Processing...' : 'Reject Selected'}
            </button>
            <button
              onClick={() => handleBatchReview(SuggestionStatus.ACCEPTED)}
              disabled={batchProcessing}
              className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-400 transition-colors font-medium"
            >
              {batchProcessing ? 'Processing...' : 'Accept Selected'}
            </button>
          </div>
        </div>
      )}

      {/* Select All / Deselect All */}
      {suggestions.length > 0 && (
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <button
              onClick={selectAll}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              Select All
            </button>
            {selectedIds.size > 0 && (
              <>
                <span className="text-gray-400">|</span>
                <button
                  onClick={clearSelection}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  Deselect All
                </button>
              </>
            )}
          </div>
          <div className="text-sm text-gray-600">
            Press <kbd className="px-2 py-1 bg-gray-100 rounded text-xs">?</kbd> for keyboard shortcuts
          </div>
        </div>
      )}

      {/* Suggestions List */}
      {suggestions.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          {hasActiveFilters ? (
            <>
              <p className="text-gray-600 text-lg mb-2">No suggestions match your filters</p>
              <button
                onClick={handleClearFilters}
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                Clear filters
              </button>
            </>
          ) : (
            <>
              <p className="text-gray-600 text-lg">🎉 All suggestions reviewed!</p>
              <p className="text-gray-500 text-sm mt-2">
                Click "Generate Suggestions" to create AI-powered link recommendations
              </p>
            </>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {suggestions.map((suggestion, index) => {
            const requirement = requirements.get(suggestion.requirement_id);
            const testCase = testCases.get(suggestion.test_case_id);

            return (
              <SuggestionCard
                key={suggestion.id}
                suggestion={suggestion}
                requirement={requirement}
                testCase={testCase}
                isSelected={selectedIds.has(suggestion.id)}
                isFocused={index === focusedIndex}
                onSelect={toggleSelection}
                onAccept={(id) => handleReview(id, SuggestionStatus.ACCEPTED)}
                onReject={(id) => handleReview(id, SuggestionStatus.REJECTED)}
                onClick={() => setPreviewSuggestion(suggestion)}
              />
            );
          })}
        </div>
      )}

      {/* Preview Modal */}
      <SuggestionPreviewModal
        isOpen={!!previewSuggestion}
        suggestion={previewSuggestion}
        requirement={previewSuggestion ? requirements.get(previewSuggestion.requirement_id) : undefined}
        testCase={previewSuggestion ? testCases.get(previewSuggestion.test_case_id) : undefined}
        onClose={() => setPreviewSuggestion(null)}
        onAccept={(id) => handleReview(id, SuggestionStatus.ACCEPTED)}
        onReject={(id) => handleReview(id, SuggestionStatus.REJECTED)}
      />

      {/* Keyboard Shortcuts Help */}
      <KeyboardShortcutsHelp isOpen={showHelp} onClose={() => setShowHelp(false)} />
    </div>
  );
};
