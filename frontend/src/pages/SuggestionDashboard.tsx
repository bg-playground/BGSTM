import React, { useCallback, useEffect, useRef, useState } from 'react';
import { suggestionsApi } from '../api/suggestions';
import { requirementsApi } from '../api/requirements';
import { testCasesApi } from '../api/testCases';
import { SuggestionStatus } from '../types/api';
import type { Suggestion, Requirement, TestCase } from '../types/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useToast } from '../components/Toast';
import { KeyboardShortcutsHelp } from '../components/KeyboardShortcutsHelp';
import { SuggestionFilters, DEFAULT_FILTERS } from '../components/SuggestionFilters';
import type { Filters } from '../components/SuggestionFilters';
import { SuggestionStats } from '../components/SuggestionStats';
import { SuggestionCard } from '../components/SuggestionCard';
import { SuggestionPreviewModal } from '../components/SuggestionPreviewModal';

export const SuggestionDashboard: React.FC = () => {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [requirements, setRequirements] = useState<Map<string, Requirement>>(new Map());
  const [testCases, setTestCases] = useState<Map<string, TestCase>>(new Map());
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [focusedIndex, setFocusedIndex] = useState<number>(-1);
  const cardRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [previewSuggestion, setPreviewSuggestion] = useState<Suggestion | null>(null);
  const { showToast } = useToast();

  // Filters state
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [suggestionData, reqData, tcData] = await Promise.all([
        suggestionsApi.listPending({
          minScore: filters.minScore,
          maxScore: filters.maxScore,
          algorithm: filters.algorithm === 'all' ? undefined : filters.algorithm,
          sortBy: filters.sortBy,
          sortOrder: filters.sortOrder
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
      </div>

      <KeyboardShortcutsHelp />

      <SuggestionFilters filters={filters} onFiltersChange={setFilters} />

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
