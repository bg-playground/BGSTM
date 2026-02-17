// TypeScript interfaces for API models

export enum RequirementType {
  FUNCTIONAL = 'FUNCTIONAL',
  NON_FUNCTIONAL = 'NON_FUNCTIONAL',
  TECHNICAL = 'TECHNICAL',
  BUSINESS = 'BUSINESS',
  SECURITY = 'SECURITY',
  PERFORMANCE = 'PERFORMANCE',
  USABILITY = 'USABILITY',
}

export enum PriorityLevel {
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
}

export enum RequirementStatus {
  DRAFT = 'DRAFT',
  APPROVED = 'APPROVED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  DEPRECATED = 'DEPRECATED',
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
  FUNCTIONAL = 'FUNCTIONAL',
  INTEGRATION = 'INTEGRATION',
  SYSTEM = 'SYSTEM',
  ACCEPTANCE = 'ACCEPTANCE',
  REGRESSION = 'REGRESSION',
  SMOKE = 'SMOKE',
  PERFORMANCE = 'PERFORMANCE',
  SECURITY = 'SECURITY',
  USABILITY = 'USABILITY',
  API = 'API',
}

export enum TestCaseStatus {
  DRAFT = 'DRAFT',
  READY = 'READY',
  IN_PROGRESS = 'IN_PROGRESS',
  PASSED = 'PASSED',
  FAILED = 'FAILED',
  BLOCKED = 'BLOCKED',
  SKIPPED = 'SKIPPED',
  DEPRECATED = 'DEPRECATED',
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
  COVERS = 'COVERS',
  VERIFIES = 'VERIFIES',
  VALIDATES = 'VALIDATES',
  RELATED_TO = 'RELATED_TO',
}

export enum LinkSource {
  MANUAL = 'MANUAL',
  AI_SUGGESTED = 'AI_SUGGESTED',
  IMPORTED = 'IMPORTED',
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
  TFIDF = 'TFIDF',
  KEYWORD = 'KEYWORD',
  HYBRID = 'HYBRID',
}

export enum SuggestionStatus {
  PENDING = 'PENDING',
  ACCEPTED = 'ACCEPTED',
  REJECTED = 'REJECTED',
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
