// TypeScript interfaces for API models

export enum RequirementType {
  FUNCTIONAL = 'functional',
  NON_FUNCTIONAL = 'non_functional',
  TECHNICAL = 'technical',
  BUSINESS = 'business',
  SECURITY = 'security',
  PERFORMANCE = 'performance',
  USABILITY = 'usability',
}

export enum PriorityLevel {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export enum RequirementStatus {
  DRAFT = 'draft',
  APPROVED = 'approved',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  DEPRECATED = 'deprecated',
}

export interface Requirement {
  id: string;
  external_id?: string;
  title: string;
  description: string;
  type: RequirementType;
  priority: PriorityLevel;
  status: RequirementStatus;
  module?: string;
  tags?: string[];
  custom_metadata?: Record<string, any>;
  source_system?: string;
  source_url?: string;
  created_by?: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface RequirementCreate {
  title: string;
  description: string;
  type: RequirementType;
  priority: PriorityLevel;
  status?: RequirementStatus;
  module?: string;
  tags?: string[];
  custom_metadata?: Record<string, any>;
  source_system?: string;
  source_url?: string;
  created_by?: string;
  external_id?: string;
}

export interface RequirementUpdate {
  title?: string;
  description?: string;
  type?: RequirementType;
  priority?: PriorityLevel;
  status?: RequirementStatus;
  module?: string;
  tags?: string[];
  custom_metadata?: Record<string, any>;
  source_system?: string;
  source_url?: string;
}

export enum TestCaseType {
  FUNCTIONAL = 'functional',
  INTEGRATION = 'integration',
  SYSTEM = 'system',
  ACCEPTANCE = 'acceptance',
  REGRESSION = 'regression',
  SMOKE = 'smoke',
  PERFORMANCE = 'performance',
  SECURITY = 'security',
  USABILITY = 'usability',
  API = 'api',
  UI = 'ui',
}

export enum TestCaseStatus {
  DRAFT = 'draft',
  READY = 'ready',
  IN_PROGRESS = 'in_progress',
  EXECUTING = 'executing',
  PASSED = 'passed',
  FAILED = 'failed',
  BLOCKED = 'blocked',
  SKIPPED = 'skipped',
  DEPRECATED = 'deprecated',
}

export interface TestCase {
  id: string;
  external_id?: string;
  title: string;
  description: string;
  type: TestCaseType;
  priority: PriorityLevel;
  status: TestCaseStatus;
  preconditions?: string;
  test_steps?: string;
  expected_result?: string;
  actual_result?: string;
  module?: string;
  tags?: string[];
  automated: boolean;
  automation_script?: string;
  estimated_duration_minutes?: number;
  custom_metadata?: Record<string, any>;
  created_by?: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface TestCaseCreate {
  title: string;
  description: string;
  type: TestCaseType;
  priority: PriorityLevel;
  status?: TestCaseStatus;
  preconditions?: string;
  test_steps?: string;
  expected_result?: string;
  actual_result?: string;
  module?: string;
  tags?: string[];
  automated?: boolean;
  automation_script?: string;
  estimated_duration_minutes?: number;
  custom_metadata?: Record<string, any>;
  created_by?: string;
  external_id?: string;
}

export interface TestCaseUpdate {
  title?: string;
  description?: string;
  type?: TestCaseType;
  priority?: PriorityLevel;
  status?: TestCaseStatus;
  preconditions?: string;
  test_steps?: string;
  expected_result?: string;
  actual_result?: string;
  module?: string;
  tags?: string[];
  automated?: boolean;
  automation_script?: string;
  estimated_duration_minutes?: number;
  custom_metadata?: Record<string, any>;
}

export enum LinkType {
  COVERS = 'covers',
  VERIFIES = 'verifies',
  VALIDATES = 'validates',
  RELATED_TO = 'related',
}

export enum LinkSource {
  MANUAL = 'manual',
  AI_SUGGESTED = 'ai_suggested',
  AI_CONFIRMED = 'ai_confirmed',
  IMPORTED = 'imported',
}

export interface Link {
  id: string;
  requirement_id: string;
  test_case_id: string;
  link_type: LinkType;
  link_source: LinkSource;
  confidence_score?: number;
  notes?: string;
  created_at: string;
  created_by?: string;
  confirmed_at?: string;
  confirmed_by?: string;
}

export interface LinkCreate {
  requirement_id: string;
  test_case_id: string;
  link_type?: LinkType;
  link_source?: LinkSource;
  confidence_score?: number;
  notes?: string;
  created_by?: string;
}

export enum SuggestionMethod {
  TFIDF = 'tfidf',
  KEYWORD = 'keyword',
  SEMANTIC_SIMILARITY = 'semantic_similarity',
  KEYWORD_MATCH = 'keyword_match',
  HEURISTIC = 'heuristic',
  HYBRID = 'hybrid',
}

export enum SuggestionStatus {
  PENDING = 'pending',
  ACCEPTED = 'accepted',
  REJECTED = 'rejected',
}

export interface Suggestion {
  id: string;
  requirement_id: string;
  test_case_id: string;
  similarity_score: number;
  suggestion_method: SuggestionMethod;
  suggestion_reason?: string;
  suggestion_metadata?: Record<string, any>;
  status: SuggestionStatus;
  created_at: string;
  reviewed_at?: string;
  reviewed_by?: string;
  feedback?: string;
}

export interface SuggestionReview {
  status: SuggestionStatus;
  feedback?: string;
  reviewed_by?: string;
}

export interface GenerateSuggestionsResponse {
  message: string;
  results: {
    pairs_analyzed: number;
    suggestions_created: number;
    suggestions_skipped: number;
    algorithm_used: string;
    threshold: number;
  };
}
