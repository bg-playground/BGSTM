-- BGSTM AI Traceability SQLite Schema
-- Version: 2.0.0
-- Note: SQLite does not support ENUM types, so we use CHECK constraints instead

-- Requirements Table
CREATE TABLE requirements (
    id TEXT PRIMARY KEY,
    external_id TEXT UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('functional', 'non_functional', 'technical')),
    priority TEXT NOT NULL CHECK(priority IN ('critical', 'high', 'medium', 'low')),
    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft', 'approved', 'implemented', 'tested', 'closed')),
    module TEXT,
    tags TEXT,  -- JSON array as TEXT
    metadata TEXT,  -- JSON object as TEXT
    source_system TEXT,
    source_url TEXT,
    created_by TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Test Cases Table
CREATE TABLE test_cases (
    id TEXT PRIMARY KEY,
    external_id TEXT UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('functional', 'integration', 'performance', 'security', 'ui', 'regression')),
    priority TEXT NOT NULL CHECK(priority IN ('critical', 'high', 'medium', 'low')),
    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft', 'ready', 'executing', 'passed', 'failed', 'blocked', 'deprecated')),
    steps TEXT,  -- JSON object as TEXT
    preconditions TEXT,
    postconditions TEXT,
    test_data TEXT,  -- JSON object as TEXT
    module TEXT,
    tags TEXT,  -- JSON array as TEXT
    automation_status TEXT DEFAULT 'manual' CHECK(automation_status IN ('manual', 'automated', 'automatable')),
    execution_time_minutes INTEGER,
    metadata TEXT,  -- JSON object as TEXT
    source_system TEXT,
    source_url TEXT,
    created_by TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Requirement-Test Case Links Table
CREATE TABLE requirement_test_case_links (
    id TEXT PRIMARY KEY,
    requirement_id TEXT NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    test_case_id TEXT NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    link_type TEXT NOT NULL DEFAULT 'covers' CHECK(link_type IN ('covers', 'verifies', 'validates', 'related')),
    confidence_score REAL,
    link_source TEXT NOT NULL CHECK(link_source IN ('manual', 'ai_suggested', 'ai_confirmed', 'imported')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    confirmed_at TIMESTAMP,
    confirmed_by TEXT,
    notes TEXT,
    UNIQUE(requirement_id, test_case_id)
);

-- Link Suggestions Table
CREATE TABLE link_suggestions (
    id TEXT PRIMARY KEY,
    requirement_id TEXT NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    test_case_id TEXT NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    similarity_score REAL NOT NULL,
    suggestion_method TEXT NOT NULL CHECK(suggestion_method IN ('semantic_similarity', 'keyword_match', 'heuristic', 'hybrid')),
    suggestion_reason TEXT,
    suggestion_metadata TEXT,  -- JSON object as TEXT
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'rejected', 'expired')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewed_by TEXT,
    feedback TEXT
);

-- Indexes for Performance
CREATE INDEX idx_requirements_external_id ON requirements(external_id);
CREATE INDEX idx_requirements_title ON requirements(title);
CREATE INDEX idx_requirements_status ON requirements(status);
CREATE INDEX idx_requirements_module ON requirements(module);

CREATE INDEX idx_test_cases_external_id ON test_cases(external_id);
CREATE INDEX idx_test_cases_title ON test_cases(title);
CREATE INDEX idx_test_cases_status ON test_cases(status);
CREATE INDEX idx_test_cases_module ON test_cases(module);

CREATE INDEX idx_links_requirement_id ON requirement_test_case_links(requirement_id);
CREATE INDEX idx_links_test_case_id ON requirement_test_case_links(test_case_id);

CREATE INDEX idx_suggestions_requirement_id ON link_suggestions(requirement_id);
CREATE INDEX idx_suggestions_test_case_id ON link_suggestions(test_case_id);
CREATE INDEX idx_suggestions_status ON link_suggestions(status);

-- Triggers for updated_at (SQLite specific)
CREATE TRIGGER update_requirements_updated_at 
AFTER UPDATE ON requirements
FOR EACH ROW
BEGIN
    UPDATE requirements SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_test_cases_updated_at 
AFTER UPDATE ON test_cases
FOR EACH ROW
BEGIN
    UPDATE test_cases SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
