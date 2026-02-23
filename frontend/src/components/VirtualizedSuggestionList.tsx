import React from 'react';
import { List } from 'react-window';
import { SuggestionCard } from './SuggestionCard';
import { SuggestionStatus } from '../types/api';
import type { Suggestion, Requirement, TestCase } from '../types/api';

const ITEM_HEIGHT = 160;

interface RowData {
  suggestions: Suggestion[];
  requirements: Map<string, Requirement>;
  testCases: Map<string, TestCase>;
  selectedIds: Set<string>;
  focusedIndex: number;
  onToggleSelect: (id: string, checked: boolean) => void;
  onReview: (id: string, status: SuggestionStatus) => void;
  onPreview: (suggestion: Suggestion) => void;
}

interface VirtualizedSuggestionListProps extends RowData {
  height?: number;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const RowComponent = ({
  index,
  style,
  ariaAttributes: _ariaAttributes,
  suggestions,
  requirements,
  testCases,
  selectedIds,
  focusedIndex,
  onToggleSelect,
  onReview,
  onPreview,
}: {
  ariaAttributes: Record<string, unknown>;
  index: number;
  style: React.CSSProperties;
} & RowData) => {
  const suggestion = suggestions[index];
  return (
    <div style={style} className="px-1">
      <SuggestionCard
        suggestion={suggestion}
        requirement={requirements.get(suggestion.requirement_id)}
        testCase={testCases.get(suggestion.test_case_id)}
        isSelected={selectedIds.has(suggestion.id)}
        isFocused={index === focusedIndex}
        onToggleSelect={onToggleSelect}
        onReview={onReview}
        onPreview={onPreview}
      />
    </div>
  );
};

export const VirtualizedSuggestionList: React.FC<VirtualizedSuggestionListProps> = ({
  suggestions,
  requirements,
  testCases,
  selectedIds,
  focusedIndex,
  onToggleSelect,
  onReview,
  onPreview,
  height = 600,
}) => {
  return (
    <List<RowData>
      rowComponent={RowComponent}
      rowCount={suggestions.length}
      rowHeight={ITEM_HEIGHT}
      defaultHeight={height}
      style={{ width: '100%' }}
      rowProps={{
        suggestions,
        requirements,
        testCases,
        selectedIds,
        focusedIndex,
        onToggleSelect,
        onReview,
        onPreview,
      }}
    />
  );
};
