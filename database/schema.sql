-- BGSTM AI Traceability PostgreSQL Schema
-- Version: 2.0.0

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Requirement Types Enum
CREATE TYPE requirement_type AS ENUM ('functional', 'non_functional', 'technical');

-- Priority Levels Enum
CREATE TYPE priority_level AS ENUM ('critical', 'high', 'medium', 'low');

-- Requirement Status Enum
CREATE TYPE requirement_status AS ENUM ('draft', 'approved', 'implemented', 'tested', 'closed');

-- Test Case Types Enum
CREATE TYPE test_case_type AS ENUM ('functional', 'integration', 'performance', 'security', 'ui', 'regression');

-- Test Case Status Enum
CREATE TYPE test_case_status AS ENUM ('draft', 'ready', 'executing', 'passed', 'failed', 'blocked', 'deprecated');

-- Automation Status Enum
CREATE TYPE automation_status AS ENUM ('manual', 'automated', 'automatable');

-- Link Types Enum
CREATE TYPE link_type AS ENUM ('covers', 'verifies', 'validates', 'related');

-- Link Source Enum
CREATE TYPE link_source AS ENUM ('manual', 'ai_suggested', 'ai_confirmed', 'imported');

-- Suggestion Method Enum
CREATE TYPE suggestion_method AS ENUM ('semantic_similarity', 'keyword_match', 'heuristic', 'hybrid');

-- Suggestion Status Enum
CREATE TYPE suggestion_status AS ENUM ('pending', 'accepted', 'rejected', 'expired');

-- Requirements Table
CREATE TABLE requirements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(100) UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    type requirement_type NOT NULL,
    priority priority_level NOT NULL,
    status requirement_status NOT NULL DEFAULT 'draft',
    module VARCHAR(100),
    tags TEXT[],
    metadata JSONB,
    source_system VARCHAR(50),
    source_url TEXT,
    created_by VARCHAR(100),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Test Cases Table
CREATE TABLE test_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(100) UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    type test_case_type NOT NULL,
    priority priority_level NOT NULL,
    status test_case_status NOT NULL DEFAULT 'draft',
    steps JSONB,
    preconditions TEXT,
    postconditions TEXT,
    test_data JSONB,
    module VARCHAR(100),
    tags TEXT[],
    automation_status automation_status DEFAULT 'manual',
    execution_time_minutes INTEGER,
    metadata JSONB,
    source_system VARCHAR(50),
    source_url TEXT,
    created_by VARCHAR(100),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Requirement-Test Case Links Table
CREATE TABLE requirement_test_case_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requirement_id UUID NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    test_case_id UUID NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    link_type link_type NOT NULL DEFAULT 'covers',
    confidence_score FLOAT,
    link_source link_source NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    confirmed_at TIMESTAMP,
    confirmed_by VARCHAR(100),
    notes TEXT,
    CONSTRAINT uq_requirement_test_case UNIQUE (requirement_id, test_case_id)
);

-- Link Suggestions Table
CREATE TABLE link_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requirement_id UUID NOT NULL REFERENCES requirements(id) ON DELETE CASCADE,
    test_case_id UUID NOT NULL REFERENCES test_cases(id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL,
    suggestion_method suggestion_method NOT NULL,
    suggestion_reason TEXT,
    suggestion_metadata JSONB,
    status suggestion_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewed_by VARCHAR(100),
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

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_requirements_updated_at BEFORE UPDATE ON requirements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_test_cases_updated_at BEFORE UPDATE ON test_cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
