-- E2E test seed data
-- Passwords are bcrypt hashes of "password123"
-- This file is run AFTER alembic upgrade head via the backend entrypoint

-- ============================================================
-- Users
-- ============================================================
INSERT INTO users (id, email, hashed_password, full_name, role, is_active, created_at, updated_at)
VALUES
  ('00000000-0000-0000-0000-000000000001',
   'admin@test.com',
   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s9u.Ge',
   'Test Admin',
   'admin',
   true,
   NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000002',
   'reviewer@test.com',
   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s9u.Ge',
   'Test Reviewer',
   'reviewer',
   true,
   NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000003',
   'viewer@test.com',
   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s9u.Ge',
   'Test Viewer',
   'viewer',
   true,
   NOW(), NOW())
ON CONFLICT (email) DO NOTHING;

-- ============================================================
-- Requirements (5 sample)
-- ============================================================
INSERT INTO requirements (id, title, description, type, priority, status, created_at, updated_at)
VALUES
  ('10000000-0000-0000-0000-000000000001',
   'User Authentication',
   'The system must support secure user authentication using email and password.',
   'functional', 'high', 'approved', NOW(), NOW()),
  ('10000000-0000-0000-0000-000000000002',
   'Dashboard Overview',
   'The dashboard must display a summary of all traceability links and suggestions.',
   'functional', 'medium', 'approved', NOW(), NOW()),
  ('10000000-0000-0000-0000-000000000003',
   'Export Traceability Matrix',
   'Users must be able to export the traceability matrix as a PDF.',
   'functional', 'medium', 'draft', NOW(), NOW()),
  ('10000000-0000-0000-0000-000000000004',
   'Role-Based Access Control',
   'The system must enforce role-based access control for all protected endpoints.',
   'functional', 'high', 'approved', NOW(), NOW()),
  ('10000000-0000-0000-0000-000000000005',
   'Performance Under Load',
   'The backend API must respond within 500ms under 100 concurrent users.',
   'non_functional', 'low', 'draft', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- Test Cases (5 sample)
-- ============================================================
INSERT INTO test_cases (id, title, description, type, priority, status, automation_status, created_at, updated_at)
VALUES
  ('20000000-0000-0000-0000-000000000001',
   'TC-001: Login with valid credentials',
   'Verify that a user can log in with valid email and password.',
   'functional', 'high', 'ready', 'automated', NOW(), NOW()),
  ('20000000-0000-0000-0000-000000000002',
   'TC-002: Login with invalid credentials',
   'Verify that an error message is shown for invalid credentials.',
   'functional', 'high', 'ready', 'automated', NOW(), NOW()),
  ('20000000-0000-0000-0000-000000000003',
   'TC-003: Export PDF report',
   'Verify that the traceability matrix can be exported as a PDF.',
   'functional', 'medium', 'draft', 'manual', NOW(), NOW()),
  ('20000000-0000-0000-0000-000000000004',
   'TC-004: Role enforcement for admin actions',
   'Verify that only admin users can access administrative features.',
   'functional', 'high', 'ready', 'manual', NOW(), NOW()),
  ('20000000-0000-0000-0000-000000000005',
   'TC-005: API response time under load',
   'Measure API response times with 100 concurrent requests.',
   'performance', 'low', 'draft', 'manual', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- Existing links (3)
-- ============================================================
INSERT INTO requirement_test_case_links
  (id, requirement_id, test_case_id, link_type, link_source, notes, created_at)
VALUES
  ('30000000-0000-0000-0000-000000000001',
   '10000000-0000-0000-0000-000000000001',
   '20000000-0000-0000-0000-000000000001',
   'verifies', 'manual', 'Login requirement covered by login test', NOW()),
  ('30000000-0000-0000-0000-000000000002',
   '10000000-0000-0000-0000-000000000001',
   '20000000-0000-0000-0000-000000000002',
   'verifies', 'manual', 'Login requirement covered by invalid credentials test', NOW()),
  ('30000000-0000-0000-0000-000000000003',
   '10000000-0000-0000-0000-000000000004',
   '20000000-0000-0000-0000-000000000004',
   'verifies', 'manual', 'RBAC requirement covered by role enforcement test', NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- Link suggestions (2 pending: one high confidence, one low)
-- ============================================================
INSERT INTO link_suggestions
  (id, requirement_id, test_case_id, similarity_score, suggestion_method, suggestion_reason, status, created_at)
VALUES
  ('40000000-0000-0000-0000-000000000001',
   '10000000-0000-0000-0000-000000000003',
   '20000000-0000-0000-0000-000000000003',
   0.92,
   'hybrid',
   'High keyword and semantic overlap between export requirement and export test case.',
   'pending',
   NOW()),
  ('40000000-0000-0000-0000-000000000002',
   '10000000-0000-0000-0000-000000000005',
   '20000000-0000-0000-0000-000000000005',
   0.41,
   'keyword_match',
   'Partial keyword overlap on performance-related terms.',
   'pending',
   NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- Notifications (1 seeded unread for reviewer)
-- ============================================================
INSERT INTO notifications (id, user_id, type, title, message, read, created_at)
VALUES
  ('50000000-0000-0000-0000-000000000001',
   '00000000-0000-0000-0000-000000000002',
   'requirement_created',
   'New requirement created',
   'Requirement "User Authentication" was created.',
   false,
   NOW())
ON CONFLICT (id) DO NOTHING;
