# Implementation Plan: Platform Audit

## Overview

Build a Python-based audit runner that systematically inspects the TelcoRetain codebase across 15 phases, combining static analysis (AST parsing, file inspection, pattern matching) with runtime verification (endpoint invocation, timing measurement). Each phase produces scored findings that feed into a final consolidated markdown report with a weighted scorecard and prioritized remediation list.

## Tasks

- [x] 1. Set up audit framework and core infrastructure
  - [x] 1.1 Create audit project structure and base classes
    - Create `backend/audit/` directory with `__init__.py`
    - Implement `AuditFinding`, `PhaseResult`, `Severity` dataclasses/enums in `backend/audit/models.py`
    - Implement `AuditPhase` abstract base class in `backend/audit/phase.py`
    - Implement `AuditRunner` orchestrator in `backend/audit/runner.py`
    - _Requirements: 15.6_

  - [x] 1.2 Implement static analysis utilities
    - Create `backend/audit/utils/static_analyzer.py` with `count_files`, `parse_python_module`, `find_class_definitions`, `find_function_definitions`, `grep_pattern`, `check_imports`
    - _Requirements: 1.1, 1.2, 1.3, 3.1, 3.2_

  - [x] 1.3 Implement runtime verifier utilities
    - Create `backend/audit/utils/runtime_verifier.py` with async HTTP client, `measure_response_time`, `check_health`
    - _Requirements: 11.1, 12.1_

  - [x] 1.4 Implement security scanner utilities
    - Create `backend/audit/utils/security_scanner.py` with `scan_for_secrets`, `check_dependency_vulnerabilities`, `check_npm_vulnerabilities`, secret pattern definitions
    - _Requirements: 9.6, 13.5, 13.7_

  - [x] 1.5 Implement report generator
    - Create `backend/audit/report_generator.py` with markdown rendering logic
    - Implement executive summary, per-phase sections, scorecard table, and prioritized remediation list
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

  - [x] 1.6 Write property tests for scoring and classification logic
    - **Property 15: Weighted Scorecard Calculation**
    - **Property 16: Readiness Classification Correctness**
    - **Validates: Requirements 15.2, 15.3**

- [x] 2. Checkpoint - Ensure framework tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Implement Phases 1-4 (Structure and Architecture)
  - [x] 3.1 Implement Phase 1: Requirement Validation
    - Create `backend/audit/phases/phase_01_requirements.py`
    - Count routers, services, repositories, screens, tables, test files, roles, ML artifacts
    - Compare counts against README baselines (11 routers, 12 services, 11 repos, 22 screens, 22 tables, 15 tests, 6 roles, 4 ML artifacts)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_

  - [x] 3.2 Implement Phase 2: Frontend Validation
    - Create `backend/audit/phases/phase_02_frontend.py`
    - Run `npx tsc --noEmit` and parse output for TypeScript errors
    - Parse `App.tsx` for route definitions and count unique paths
    - Verify `<Protected>` wrapper usage on authenticated routes
    - Check for localStorage token persistence without expiration
    - Grep for hardcoded URLs, secrets, and credentials in frontend source
    - Verify API client error interceptors
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 3.3 Implement Phase 3: Backend Validation
    - Create `backend/audit/phases/phase_03_backend.py`
    - AST-verify router→service delegation pattern for each router file
    - AST-verify service→repository pattern for each service file
    - Verify `response_model` and request body type hints on endpoint functions
    - Check middleware registration order in `main.py`
    - Verify `async with` pattern for all `AsyncSessionLocal` usages
    - Identify list endpoints and verify `limit`/`offset` parameters
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [x] 3.4 Write property tests for architectural pattern detection
    - **Property 1: Layered Delegation — Routers to Services**
    - **Property 2: Repository Pattern Enforcement**
    - **Property 3: Schema Validation Coverage**
    - **Property 4: Async Session Safety**
    - **Property 5: List Endpoint Pagination**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.6, 3.7**

  - [x] 3.5 Implement Phase 4: Database Validation
    - Create `backend/audit/phases/phase_04_database.py`
    - Parse ORM models, extract `__tablename__` attributes, compare against 22-table claim
    - Inspect Alembic migration for `op.create_table()` calls
    - Check ForeignKey columns for `ondelete`/`onupdate` cascade params
    - Verify `unique=True` on email/username columns
    - Verify `index=True` on customer_id, user_id, created_at columns
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [x] 3.6 Write property test for foreign key cascade definitions
    - **Property 6: Foreign Key Cascade Definitions**
    - **Validates: Requirements 4.3**

- [ ] 4. Implement Phases 5-8 (Data and ML)
  - [x] 4.1 Implement Phase 5: Dataset Validation
    - Create `backend/audit/phases/phase_05_dataset.py`
    - Load and validate CSV schema against IBM Telco Customer Churn expected columns
    - Parse preprocessing code for encoder instantiation and category coverage
    - Compare feature columns between training and inference pipelines
    - Check dataset upload endpoint for schema validation logic
    - Inspect preprocessing for explicit null/imputation handling per column
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ] 4.2 Write property tests for dataset validation checks
    - **Property 7: Categorical Encoding Completeness**
    - **Property 8: Null Handling Completeness**
    - **Validates: Requirements 5.2, 5.5**

  - [x] 4.3 Implement Phase 6: ML Model Validation
    - Create `backend/audit/phases/phase_06_ml_model.py`
    - Check ML artifacts directory for versioning metadata (training_date, dataset_hash, hyperparameters)
    - Verify graceful handling of missing/corrupted model artifacts in loader code
    - Check LightGBM artifact existence (report as Critical if missing)
    - Inspect prediction service for documented ensemble logic
    - Verify model versioning (no overwrite on retrain)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [x] 4.4 Implement Phase 7: SHAP Validation
    - Create `backend/audit/phases/phase_07_shap.py`
    - Verify `shap.TreeExplainer` instantiation with correct model object
    - Inspect explanation output structure for `feature_name`, `shap_value`, `direction` fields
    - Check edge case handling (zero-variance features, missing features)
    - Verify `reason_map` covers top features from training data
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ] 4.5 Write property tests for SHAP validation
    - **Property 9: SHAP Additivity**
    - **Property 10: Explanation Response Completeness**
    - **Validates: Requirements 7.2, 7.3**

  - [x] 4.6 Implement Phase 8: Recommendation Engine Validation
    - Create `backend/audit/phases/phase_08_recommendations.py`
    - Verify `match_offers()` signature takes `churn_probability` and `risk_category`
    - Verify offer_type values include "discount", "data_bonus", "plan_upgrade"
    - Verify branching logic uses `customer.arpu` and `risk_category`
    - Verify low-risk path produces minimal offers
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ] 4.7 Write property test for recommendation personalization
    - **Property 11: Recommendation Personalization**
    - **Validates: Requirements 8.3, 8.4**

- [ ] 5. Checkpoint - Ensure Phases 1-8 pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement Phases 9-10 (Authentication and Authorization)
  - [ ] 6.1 Implement Phase 9: Authentication Validation
    - Create `backend/audit/phases/phase_09_authentication.py`
    - Verify JWT algorithm is HS256 or stronger
    - Verify `ACCESS_TOKEN_EXPIRE_MINUTES` is bounded (≤ 60)
    - Verify JWT payload includes `sub`, `exp`, `iat` claims
    - Verify `bcrypt.gensalt()` usage with rounds ≥ 10
    - Search for account lockout logic (5 failed attempts / 15-min window)
    - Verify `blacklist_token` on logout and `is_token_blacklisted` check on auth
    - Verify refresh token expiration > access token expiration
    - Grep for `SECRET_KEY` with literal values in non-.env files (Critical if found)
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ] 6.2 Implement Phase 10: RBAC Validation
    - Create `backend/audit/phases/phase_10_rbac.py`
    - Parse role model/enum for 6 distinct role values
    - For each router with `Depends(get_current_user)`: verify `require_role` is present
    - Inspect endpoints with resource IDs for ownership validation (IDOR check)
    - Verify admin router uses `require_role(["Super Admin", "Admin"])`
    - Check role-update endpoint for admin-only guard
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ] 6.3 Write property test for RBAC enforcement coverage
    - **Property 12: RBAC Enforcement Coverage**
    - **Validates: Requirements 10.2**

- [ ] 7. Implement Phases 11-12 (E2E and Performance)
  - [ ] 7.1 Implement Phase 11: End-to-End Flow Testing
    - Create `backend/audit/phases/phase_11_e2e.py`
    - Test registration → login → access protected endpoint flow
    - Test customer selection → prediction → SHAP explanation → recommendations flow
    - Test campaign creation → target assignment → analytics retrieval flow
    - Test admin user list → role update → audit log viewing flow
    - Test model metrics retrieval → retrain trigger flow
    - Handle server-unreachable gracefully (report all checks as failed with note)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [ ] 7.2 Implement Phase 12: Performance Testing
    - Create `backend/audit/phases/phase_12_performance.py`
    - Measure response times for `/health`, `/auth/login`, `/customers`, `/predictions` (flag if > 2s)
    - AST-scan repository methods for loops containing queries (N+1 detection)
    - Time bulk prediction endpoint with 100 customer payloads (flag if > 10s)
    - Verify rate limit settings match claims (10/min, 60/min, 120/min)
    - Check for caching decorators or query optimization on dashboard endpoints
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 8. Implement Phases 13-14 (Security and Quality)
  - [ ] 8.1 Implement Phase 13: Security Testing
    - Create `backend/audit/phases/phase_13_security.py`
    - Verify all endpoint parameters use Pydantic types (no raw `str` from query without validation)
    - Check response middleware for security headers (X-Content-Type-Options, X-Frame-Options, HSTS)
    - Verify `CORS_ORIGINS` doesn't contain `"*"`
    - Verify exception handlers don't include `traceback` in response
    - Run `pip-audit` on requirements.txt, `npm audit` on package.json
    - Check dataset upload endpoint for file type/size validation
    - Grep for database URLs, API keys in `.py`/`.ts` files (excluding `.env`)
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7_

  - [ ] 8.2 Implement Phase 14: Code Quality Review
    - Create `backend/audit/phases/phase_14_code_quality.py`
    - Parse test files, verify they contain `def test_*` with `assert` statements (not empty)
    - Compute docstring coverage: count public functions with/without docstrings
    - Grep for hardcoded numeric literals (timeouts, limits) not sourced from settings
    - Check `except` blocks for structured logging (structlog calls with context)
    - Run `ruff` for unused imports and dead code detection
    - Check for absence of test config/files in frontend
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_

  - [ ] 8.3 Write property tests for code quality checks
    - **Property 13: Documentation Coverage**
    - **Property 14: Configuration Externalization**
    - **Validates: Requirements 14.2, 14.3**

- [ ] 9. Implement Phase 15 and wire everything together
  - [ ] 9.1 Implement Phase 15: Final Scorecard aggregation
    - Create `backend/audit/phases/phase_15_scorecard.py`
    - Compute `Phase_Score = (passed_checks / total_checks) × 10` for each phase
    - Apply weights: Security (Phase 13) × 1.5, Authentication (Phase 9) × 1.5, Code Quality (Phase 14) × 0.75
    - Compute weighted average for overall score
    - Classify readiness per thresholds (8.0+, 6.0-7.9, 4.0-5.9, <4.0)
    - Generate prioritized remediation list (Critical first, then High)
    - Render summary table with counts by severity
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

  - [ ] 9.2 Wire phase registry and CLI entry point
    - Create `backend/audit/phases/__init__.py` registering all 15 phases
    - Create `backend/audit/__main__.py` CLI entry point accepting `--workspace` arg
    - Wire `AuditRunner` to load all phases, execute in sequence, output final report to `audit_report.md`
    - _Requirements: 15.6_

  - [ ] 9.3 Write unit tests for report generator output format
    - Verify markdown output contains required sections (executive summary, per-phase, scorecard, remediation)
    - Test with fixture findings for correct severity grouping
    - _Requirements: 15.4, 15.5, 15.6_

- [ ] 10. Final checkpoint - Run full audit and validate report
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The audit runner is designed as a standalone tool within the backend directory
- Runtime verification phases (11, 12) require the server to be running and will gracefully handle unavailability
- The LightGBM artifact is known to be missing — the audit should flag this as a Critical finding

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "1.3", "1.4"] },
    { "id": 2, "tasks": ["1.5", "1.6"] },
    { "id": 3, "tasks": ["3.1", "3.2", "3.3", "3.5"] },
    { "id": 4, "tasks": ["3.4", "3.6", "4.1", "4.3", "4.4", "4.6"] },
    { "id": 5, "tasks": ["4.2", "4.5", "4.7", "6.1", "6.2"] },
    { "id": 6, "tasks": ["6.3", "7.1", "7.2"] },
    { "id": 7, "tasks": ["8.1", "8.2"] },
    { "id": 8, "tasks": ["8.3", "9.1"] },
    { "id": 9, "tasks": ["9.2"] },
    { "id": 10, "tasks": ["9.3"] }
  ]
}
```
