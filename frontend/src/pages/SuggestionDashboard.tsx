import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { suggestionsApi } from '../api/suggestions';
import traceabilityApi from '../api/traceability';
import { requirementsApi } from '../api/requirements';
import { testCasesApi } from '../api/testCases';
import { SuggestionStatus } from '../types/api';
import type { Suggestion, Requirement, TestCase } from '../types/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useToast } from '../context/ToastContext';
import { KeyboardShortcutsHelp } from '../components/KeyboardShortcutsHelp';
import { SuggestionFilters } from '../components/SuggestionFilters';
import { DEFAULT_FILTERS } from '../types/filters';
import type { Filters } from '../types/filters';
import { SuggestionStats } from '../components/SuggestionStats';
import { SuggestionCard } from '../components/SuggestionCard';
import { SuggestionPreviewModal } from '../components/SuggestionPreviewModal';

const STORAGE_KEY = 'bgstm-suggestion-filters';

const VALID_ALGORITHMS = new Set(['all', 'tfidf', 'keyword', 'hybrid', 'llm']);
const VALID_SORT_BY = new Set(['score', 'date', 'algorithm']);
const VALID_SORT_ORDER = new Set(['asc', 'desc']);

function readFromStorage(): Partial<Filters> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    return JSON.parse(raw) as Partial<Filters>;
  } catch {
    return {};
  }
}

function writeToStorage(filters: Filters): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filters));
  } catch {
    // Ignore (e.g. private browsing)
  }
}

function clearStorage(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignore
  }
}

function parseFiltersFromParams(params: URLSearchParams, stored: Partial<Filters>): Filters {
  const minScoreRaw = params.get('min_score');
  const maxScoreRaw = params.get('max_score');
  const algorithmRaw = params.get('algorithm');
  const sortByRaw = params.get('sort_by');
  const sortOrderRaw = params.get('sort_order');
  const searchRaw = params.get('search');

  const minScore = minScoreRaw !== null ? parseFloat(minScoreRaw) : null;
  const maxScore = maxScoreRaw !== null ? parseFloat(maxScoreRaw) : null;

  return {
    minScore:
      minScore !== null && !isNaN(minScore) && minScore >= 0 && minScore <= 1
        ? minScore
        : (stored.minScore ?? DEFAULT_FILTERS.minScore),
    maxScore:
      maxScore !== null && !isNaN(maxScore) && maxScore >= 0 && maxScore <= 1
        ? maxScore
        : (stored.maxScore ?? DEFAULT_FILTERS.maxScore),
    algorithm:
      algorithmRaw && VALID_ALGORITHMS.has(algorithmRaw)
        ? algorithmRaw
        : (stored.algorithm ?? DEFAULT_FILTERS.algorithm),
    sortBy:
      sortByRaw && VALID_SORT_BY.has(sortByRaw)
        ? sortByRaw
        : (stored.sortBy ?? DEFAULT_FILTERS.sortBy),
    sortOrder:
      sortOrderRaw && VALID_SORT_ORDER.has(sortOrderRaw)
        ? sortOrderRaw
        : (stored.sortOrder ?? DEFAULT_FILTERS.sortOrder),
    search: searchRaw !== null ? searchRaw : (stored.search ?? DEFAULT_FILTERS.search),
  };
}

export const SuggestionDashboard: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [requirements, setRequirements] = useState<Map<string, Requirement>>(new Map());
  const [testCases, setTestCases] = useState<Map<string, TestCase>>(new Map());
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const cardRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [previewSuggestion, setPreviewSuggestion] = useState<Suggestion | null>(null);
  const { showToast } = useToast();

  // Filters state: priority URL params > localStorage > defaults
  const [filters, setFilters] = useState<Filters>(() =>
    parseFiltersFromParams(searchParams, readFromStorage())
  );

  // Sync URL params when filters change
  const syncFiltersToUrl = useCallback(
    (f: Filters) => {
      const params = new URLSearchParams();
      if (f.minScore !== DEFAULT_FILTERS.minScore) params.set('min_score', f.minScore.toString());
      if (f.maxScore !== DEFAULT_FILTERS.maxScore) params.set('max_score', f.maxScore.toString());
      if (f.algorithm !== DEFAULT_FILTERS.algorithm) params.set('algorithm', f.algorithm);
      if (f.sortBy !== DEFAULT_FILTERS.sortBy) params.set('sort_by', f.sortBy);
      if (f.sortOrder !== DEFAULT_FILTERS.sortOrder) params.set('sort_order', f.sortOrder);
      if (f.search) params.set('search', f.search);
      setSearchParams(params, { replace: true });
    },
    [setSearchParams]
  );

  const handleFiltersChange = useCallback(
    (newFilters: Filters) => {
      setFilters(newFilters);
      writeToStorage(newFilters);
      syncFiltersToUrl(newFilters);
    },
    [syncFiltersToUrl]
  );

  const handleReset = useCallback(() => {
    clearStorage();
    setFilters(DEFAULT_FILTERS);
    setSearchParams({}, { replace: true });
  }, [setSearchParams]);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [suggestionData, reqData, tcData] = await Promise.all([
        suggestionsApi.listPending({
          minScore: filters.minScore,
          maxScore: filters.maxScore,
          algorithm: filters.algorithm === 'all' ? undefined : filters.algorithm,
          sortBy: filters.sortBy,
          sortOrder: filters.sortOrder,
          search: filters.search || undefined,
        }),
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

  // Reset focus when suggestion list changes
  useEffect(() => {
    setFocusedIndex(-1);
  }, [suggestions]);

  // Scroll focused card into view
  useEffect(() => {
    if (focusedIndex >= 0 && cardRefs.current[focusedIndex]) {
      cardRefs.current[focusedIndex]?.scrollIntoView({ block: 'nearest' });
    }
  }, [focusedIndex]);

  const handleReview = useCallback(async (id: string, status: SuggestionStatus) => {
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
  }, [showToast]);

  const handleBulkAccept = useCallback(async () => {
    try {
      await suggestionsApi.bulkReview(Array.from(selectedIds), SuggestionStatus.ACCEPTED);
      showToast(`Accepted ${selectedIds.size} suggestions`, 'success');
      setSelectedIds(new Set());
      await loadData();
    } catch {
      showToast('Failed to accept suggestions', 'error');
    }
  }, [selectedIds, showToast, loadData]);

  const handleBulkReject = useCallback(async () => {
    try {
      await suggestionsApi.bulkReview(Array.from(selectedIds), SuggestionStatus.REJECTED);
      showToast(`Rejected ${selectedIds.size} suggestions`, 'success');
      setSelectedIds(new Set());
      await loadData();
    } catch {
      showToast('Failed to reject suggestions', 'error');
    }
  }, [selectedIds, showToast, loadData]);

  const handleGenerate = useCallback(async () => {
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
  }, [showToast, loadData]);

  const handleExportCsv = useCallback(async () => {
    try {
      setExporting(true);
      const blob = await suggestionsApi.exportCsv({
        algorithm: filters.algorithm !== 'all' ? filters.algorithm : undefined,
        minScore: filters.minScore !== 0 ? filters.minScore : undefined,
        maxScore: filters.maxScore !== 1 ? filters.maxScore : undefined,
      });
      const filename = `suggestions_${new Date().toISOString().split('T')[0]}.csv`;
      traceabilityApi.downloadExport(blob, filename);
      showToast('Exported suggestions as CSV', 'success');
    } catch (error) {
      console.error('Error exporting suggestions:', error);
      showToast('Failed to export suggestions', 'error');
    } finally {
      setExporting(false);
    }
  }, [filters, showToast]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Only if not in an input field
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch(e.key) {
        case 'ArrowDown':
          e.preventDefault();
          if (suggestions.length > 0) {
            setFocusedIndex((prev) => Math.min(Math.max(prev, -1) + 1, suggestions.length - 1));
          }
          break;
        case 'ArrowUp':
          e.preventDefault();
          setFocusedIndex((prev) => (prev > 0 ? prev - 1 : prev));
          break;
        case 'a': {
          const hasFocusedCard = selectedIds.size === 0 && focusedIndex >= 0;
          if (hasFocusedCard) {
            // Accept focused card
            handleReview(suggestions[focusedIndex].id, SuggestionStatus.ACCEPTED);
          } else {
            // Select all visible
            setSelectedIds(new Set(suggestions.map(s => s.id)));
          }
          break;
        }
        case 'r': {
          const hasFocusedCard = selectedIds.size === 0 && focusedIndex >= 0;
          if (hasFocusedCard) {
            handleReview(suggestions[focusedIndex].id, SuggestionStatus.REJECTED);
          }
          break;
        }
        case 'c':
          // Clear selection
          setSelectedIds(new Set());
          break;
        case ' ':
          if (focusedIndex >= 0) {
            e.preventDefault();
            const focusedId = suggestions[focusedIndex].id;
            setSelectedIds((prev) => {
              const next = new Set(prev);
              if (next.has(focusedId)) {
                next.delete(focusedId);
              } else {
                next.add(focusedId);
              }
              return next;
            });
          }
          break;
        case 'Enter':
          if (focusedIndex >= 0 && selectedIds.size === 0) {
            // Open preview for focused suggestion
            setPreviewSuggestion(suggestions[focusedIndex]);
          } else if (selectedIds.size > 0) {
            // Accept selected
            handleBulkAccept();
          }
          break;
        case 'Delete':
        case 'Backspace':
          // Reject selected
          if (selectedIds.size > 0 && e.shiftKey) {
            e.preventDefault();
            handleBulkReject();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [suggestions, selectedIds, focusedIndex, handleBulkAccept, handleBulkReject, handleReview]);

  const handleToggleSelect = useCallback((id: string, checked: boolean) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (checked) {
        next.add(id);
      } else {
        next.delete(id);
      }
      return next;
    });
  }, []);

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
        <button
          onClick={handleExportCsv}
          disabled={exporting}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          Export CSV
        </button>
      </div>

      <KeyboardShortcutsHelp />

      <SuggestionFilters filters={filters} onFiltersChange={handleFiltersChange} onReset={handleReset} />

      <SuggestionStats suggestions={suggestions} />

      {suggestions.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <p className="text-gray-600 text-lg">No pending suggestions</p>
          <p className="text-gray-500 text-sm mt-2">
            Click "Generate Suggestions" to create AI-powered link recommendations
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {suggestions.map((suggestion, index) => (
            <SuggestionCard
              key={suggestion.id}
              ref={(el) => { cardRefs.current[index] = el; }}
              suggestion={suggestion}
              requirement={requirements.get(suggestion.requirement_id)}
              testCase={testCases.get(suggestion.test_case_id)}
              isSelected={selectedIds.has(suggestion.id)}
              isFocused={focusedIndex === index}
              onToggleSelect={handleToggleSelect}
              onReview={handleReview}
              onPreview={setPreviewSuggestion}
            />
          ))}
        </div>
      )}

      {/* Bulk action bar */}
      {selectedIds.size > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-primary-600 text-white shadow-lg p-4 flex items-center justify-between z-50">
          <div>
            <span className="font-semibold">{selectedIds.size} suggestions selected</span>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleBulkReject}
              className="px-6 py-2 bg-red-500 hover:bg-red-600 rounded-lg"
            >
              Reject Selected
            </button>
            <button
              onClick={handleBulkAccept}
              className="px-6 py-2 bg-green-500 hover:bg-green-600 rounded-lg"
            >
              Accept Selected
            </button>
            <button
              onClick={() => setSelectedIds(new Set())}
              className="px-6 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg"
            >
              Clear Selection
            </button>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {previewSuggestion && (
        <SuggestionPreviewModal
          suggestion={previewSuggestion}
          requirement={requirements.get(previewSuggestion.requirement_id)}
          testCase={testCases.get(previewSuggestion.test_case_id)}
          onClose={() => setPreviewSuggestion(null)}
          onReview={handleReview}
        />
      )}
    </div>
  );
};
