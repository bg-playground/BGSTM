export const DEFAULT_FILTERS = {
  minScore: 0,
  maxScore: 1,
  algorithm: 'all',
  sortBy: 'score',
  sortOrder: 'desc',
  search: '',
};

export type Filters = typeof DEFAULT_FILTERS;
