# Design Document: Platform Audit

## Overview

The platform audit is implemented as a Python-based audit runner that systematically inspects the TelcoRetain codebase across 15 phases. It combines **static analysis** (AST parsing, file inspection, pattern matching) with **runtime verification** (server startup, endpoint invocation, timing measurement) to produce a single consolidated markdown report with scored sections and a final scorecard.

The architecture follows a pipeline pattern where each phase is an independent audit module that receives the workspace context and emits structured findings. A report generator aggregates findings, computes scores, and renders the final markdown output.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Audit Runner                          │
│  (orchestrates phases, collects findings, scores)       │
└──────────────┬──────────────────────────────────────────┘
               │
    ┌──────────▼──────────────────────────────┐
    │         Phase Registry                   │
    │  (15 registered audit phase modules)     │
    └──────────┬──────────────────────────────-┘
               │
    ┌──────────▼──────────┐
    │   Phase Executor    │─────► StaticAnalyzer
    │   (per-phase loop)  │─────► RuntimeVerifier
    │                     │─────► SecurityScanner
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   Report Generator  │
    │   (scoring + render)│
    └─────────────────────┘
```

## Components and Interfaces

### 1. AuditRunner

The top-level orchestrator that:
- Discovers workspace paths (backend, frontend, ML directories)
- Instantiates and runs each of the 15 phase modules in sequence
- Collects `AuditFinding` objects from each phase
- Passes findings to the `ReportGenerator`

```python
class AuditRunner:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.phases: list[AuditPhase] = []
        self.findings: dict[str, list[AuditFinding]] = {}

    async def run(self) -> AuditReport:
        for phase in self.phases:
            phase_findings = await phase.execute(self.workspace_root)
            self.findings[phase.name] = phase_findings
        return ReportGenerator.generate(self.findings)
```

### 2. AuditPhase (Base Class)

Each phase implements a common interface:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

class Severity(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"

@dataclass
class AuditFinding:
    phase: str
    check_id: str
    title: str
    severity: Severity
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    recommendation: str = ""

@dataclass
class PhaseResult:
    phase_name: str
    total_checks: int
    passed_checks: int
    findings: list[AuditFinding]

    @property
    def score(self) -> float:
        """Score 0-10 based on pass ratio."""
        if self.total_checks == 0:
            return 0.0
        return round((self.passed_checks / self.total_checks) * 10, 1)

class AuditPhase(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, workspace_root: Path) -> PhaseResult:
        ...
```

### 3. Static Analyzer Utilities

Shared utilities for code inspection without execution:

```python
import ast
from pathlib import Path
from typing import Generator

class StaticAnalyzer:
    @staticmethod
    def count_files(directory: Path, pattern: str) -> int:
        """Count files matching a glob pattern."""
        return len(list(directory.glob(pattern)))

    @staticmethod
    def parse_python_module(file_path: Path) -> ast.Module:
        """Parse a Python file into an AST."""
        return ast.parse(file_path.read_text(encoding="utf-8"))

    @staticmethod
    def find_class_definitions(module: ast.Module) -> list[ast.ClassDef]:
        """Extract all class definitions from an AST module."""
        return [node for node in ast.walk(module) if isinstance(node, ast.ClassDef)]

    @staticmethod
    def find_function_definitions(module: ast.Module) -> list[ast.FunctionDef]:
        """Extract function/method definitions."""
        return [
            node for node in ast.walk(module)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

    @staticmethod
    def grep_pattern(directory: Path, pattern: str, extensions: list[str]) -> list[tuple[Path, int, str]]:
        """Search for regex pattern in files with given extensions."""
        import re
        results = []
        for ext in extensions:
            for file in directory.rglob(f"*{ext}"):
                for i, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
                    if re.search(pattern, line):
                        results.append((file, i, line.strip()))
        return results

    @staticmethod
    def check_imports(module: ast.Module, target_module: str) -> bool:
        """Check if a module imports from a target module path."""
        for node in ast.walk(module):
            if isinstance(node, ast.ImportFrom) and node.module and target_module in node.module:
                return True
        return False
```

### 4. Runtime Verifier

For phases that require the server to be running:

```python
import httpx
import time
from typing import Optional

class RuntimeVerifier:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)
        return self

    async def __aexit__(self, *args):
        if self.client:
            await self.client.aclose()

    async def measure_response_time(self, method: str, path: str, **kwargs) -> tuple[float, int]:
        """Returns (elapsed_seconds, status_code)."""
        start = time.perf_counter()
        response = await self.client.request(method, path, **kwargs)
        elapsed = time.perf_counter() - start
        return elapsed, response.status_code

    async def check_health(self) -> bool:
        """Verify server is running."""
        try:
            resp = await self.client.get("/health")
            return resp.status_code == 200
        except Exception:
            return False
```

### 5. Security Scanner

Specialized utilities for security-focused checks:

```python
class SecurityScanner:
    SECRET_PATTERNS = [
        r"(?i)(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]",
        r"(?i)Bearer\s+[A-Za-z0-9\-._~+/]+=*",
        r"postgresql://\w+:\w+@",
    ]

    SECURITY_HEADERS = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Strict-Transport-Security",
        "X-XSS-Protection",
    ]

    @classmethod
    def scan_for_secrets(cls, directory: Path, exclude_patterns: list[str]) -> list[tuple[Path, int, str]]:
        """Scan source files for hardcoded secrets."""
        ...

    @classmethod
    def check_dependency_vulnerabilities(cls, requirements_path: Path) -> list[dict]:
        """Run pip-audit or safety check on requirements."""
        ...

    @classmethod
    def check_npm_vulnerabilities(cls, package_json_path: Path) -> list[dict]:
        """Run npm audit on package.json."""
        ...
```

## Phase Implementations

### Phase 1: Requirement Validation

**Approach:** Static file counting and pattern matching.

| Check | Method | Expected |
|-------|--------|----------|
| Router count | `count_files(api/v1/, "*.py") - __init__.py - __pycache__` | 11 |
| Service count | `count_files(services/, "*.py") - __init__.py` | 12 |
| Repository count | `count_files(repositories/, "*.py") - __init__.py` | 11 |
| Screen count | `count_files(frontend/src/pages/, "*.tsx")` | 22 |
| Table count | AST parse all model files, count `__tablename__` | 22 |
| Test file count | `count_files(tests/, "test_*.py")` | 15 |
| Role count | Parse RBAC config/model for role definitions | 6 |
| ML artifact check | Verify existence of 4 model .pkl files | 4 files |

### Phase 2: Frontend Validation

**Approach:** TypeScript compilation + static source analysis.

- Run `npx tsc --noEmit` and parse output for errors
- Parse `App.tsx` for `<Route>` elements, count unique paths
- Verify `<Protected>` wrapper around authenticated routes
- Grep for `localStorage` usage in state stores
- Grep for hardcoded URLs/secrets (`/https?:\/\/(?!localhost)/`, API key patterns)
- Inspect API client for error interceptors

### Phase 3: Backend Validation

**Approach:** Python AST analysis of architectural patterns.

- For each router file: verify it imports from `services/` and calls service methods
- For each service file: verify it imports from `repositories/` and uses repo methods
- For each endpoint function: check for `response_model` parameter and request body type hints
- Parse `main.py` middleware registration order
- Grep for `AsyncSessionLocal` usage, verify `async with` pattern
- Identify list endpoints (returning `list[...]`), check for `limit`/`offset` params

### Phase 4: Database Validation

**Approach:** AST parsing of ORM models + Alembic migration inspection.

- Parse all files in `models/`, extract `__tablename__` attributes
- Parse Alembic migration for `op.create_table()` calls
- For each `ForeignKey` column: check for `ondelete`/`onupdate` cascade params
- Check `email`/`username` columns for `unique=True`
- Check `customer_id`, `user_id`, `created_at` for `index=True`

### Phase 5: Dataset Validation

**Approach:** CSV schema validation + preprocessing code inspection.

- Load `WA_Fn-UseC_-Telco-Customer-Churn.csv`, verify columns match IBM Telco schema
- Parse preprocessing code for encoder instantiation, verify categories covered
- Compare feature column lists between training script and inference pipeline
- Check dataset upload endpoint for schema validation logic
- Inspect preprocessing for explicit `fillna`/imputation per column

### Phase 6: ML Model Validation

**Approach:** Artifact inspection + code path analysis.

- Parse `metadata.json` for required fields (training_date, dataset_hash, hyperparameters)
- Check `ModelRegistry.initialize()` for try/except around file loading
- Verify `lightgbm.pkl` existence (CRITICAL if missing)
- Inspect prediction service for ensemble logic documentation
- If runtime available: load model + test data, compute AUC
- Check for version incrementing in model save logic

### Phase 7: SHAP Validation

**Approach:** Code inspection + mathematical property verification.

- Verify `shap.TreeExplainer(self._model)` call with model object
- If runtime available: compute SHAP values and verify additivity (sum ≈ prediction - base)
- Verify explanation output structure includes `feature_name`, `shap_value`, direction
- Test edge cases: empty feature dict, zero-variance inputs
- Verify `reason_map` covers top features from training data

### Phase 8: Recommendation Engine Validation

**Approach:** Code inspection + logic analysis.

- Verify `match_offers()` signature takes `churn_probability` and `risk_category`
- Verify offer_type values include "discount", "data_bonus", "plan_upgrade"
- Verify branching logic uses `customer.arpu` and `risk_category`
- Verify low-risk path (churn_probability < 0.7, risk_category != "HIGH") produces minimal offers

### Phase 9: Authentication Validation

**Approach:** Security module code inspection.

- Verify `settings.ALGORITHM` is "HS256" or stronger
- Verify `ACCESS_TOKEN_EXPIRE_MINUTES` is bounded (≤ 60)
- Verify JWT payload includes `sub`, `exp`, `iat` claims
- Verify `bcrypt.gensalt()` usage (default rounds ≥ 10)
- Search for account lockout logic in auth service
- Verify `blacklist_token` called on logout, `is_token_blacklisted` checked on auth
- Verify `REFRESH_TOKEN_EXPIRE_DAYS > ACCESS_TOKEN_EXPIRE_MINUTES / (60*24)`
- Grep for `SECRET_KEY` with literal values in non-.env files

### Phase 10: RBAC Validation

**Approach:** Code inspection of role definitions and enforcement.

- Parse role model/enum for 6 distinct values
- For each router file with `Depends(get_current_user)`: verify `require_role` is also present
- Inspect endpoints taking resource IDs for ownership validation
- Verify admin router uses `require_role(["Super Admin", "Admin"])`
- Check role-update endpoint for admin-only guard

### Phase 11: End-to-End Flow Testing

**Approach:** Runtime verification via sequential API calls.

- Registration → Login → Access protected endpoint
- Select customer → Request prediction → Get SHAP explanation → Get recommendations
- Create campaign → Assign targets → Get analytics
- Admin: list users → update role → view audit logs
- Get model metrics → trigger retrain (if endpoint exists)

### Phase 12: Performance Testing

**Approach:** Runtime measurement + static query analysis.

- Measure response times for `/health`, `/auth/login`, `/customers`, `/predictions`
- AST-scan repository methods for loops containing queries (N+1 detection)
- Time bulk prediction endpoint with 100 customer payloads
- Verify `RATE_LIMIT_*` settings match "10/minute", "60/minute", "120/minute"
- Check for caching decorators or query optimization in dashboard endpoints

### Phase 13: Security Testing

**Approach:** Combined static + runtime security checks.

- Verify all endpoint parameters use Pydantic types (no raw `str` from query)
- Check response middleware for security headers
- Verify `CORS_ORIGINS` doesn't contain `"*"`
- Verify exception handlers don't include `traceback` in response
- Run `pip-audit` on requirements.txt, `npm audit` on package.json
- Check dataset upload endpoint for file type/size validation
- Grep for database URLs, API keys in `.py`/`.ts` files (excluding `.env`)

### Phase 14: Code Quality Review

**Approach:** Static analysis + tooling output.

- Parse test files, verify they contain `def test_*` with `assert` statements
- Compute docstring coverage: count public functions with/without docstrings
- Grep for hardcoded numeric literals (timeouts, limits) not from settings
- Check `except` blocks for structured logging (structlog calls with context)
- Run `ruff` for unused imports and dead code
- Check for absence of test config/files in frontend

### Phase 15: Final Scorecard

**Approach:** Aggregation and calculation.

- Compute `Phase_Score = (passed_checks / total_checks) * 10` for each phase
- Apply weights: Security (Phase 13) × 1.5, Authentication (Phase 9) × 1.5, Code Quality (Phase 14) × 0.75
- Compute weighted average for overall score
- Classify readiness per thresholds (8.0+, 6.0-7.9, 4.0-5.9, <4.0)
- Generate prioritized remediation list (Critical first, then High)
- Render summary table with counts by severity

## Data Models

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class AuditReport:
    phases: list[PhaseResult]
    overall_score: float
    readiness_classification: str
    total_critical: int
    total_high: int
    total_medium: int
    remediation_list: list[AuditFinding]

    @property
    def weighted_score(self) -> float:
        """Compute weighted overall score."""
        weights = {
            "Authentication Validation": 1.5,
            "Security Testing": 1.5,
            "Code Quality Review": 0.75,
        }
        total_weight = 0.0
        weighted_sum = 0.0
        for phase in self.phases:
            w = weights.get(phase.phase_name, 1.0)
            weighted_sum += phase.score * w
            total_weight += w
        return round(weighted_sum / total_weight, 2) if total_weight else 0.0

    @property
    def readiness(self) -> str:
        score = self.weighted_score
        if score >= 8.0:
            return "Production Ready"
        elif score >= 6.0:
            return "Production Ready with Caveats"
        elif score >= 4.0:
            return "Significant Rework Required"
        else:
            return "Not Production Ready"
```

```python
@dataclass
class PhaseResult:
    phase_name: str
    total_checks: int
    passed_checks: int
    findings: list[AuditFinding] = field(default_factory=list)

    @property
    def score(self) -> float:
        if self.total_checks == 0:
            return 0.0
        return round((self.passed_checks / self.total_checks) * 10, 1)
```

## Report Generation

The `ReportGenerator` renders the final markdown:

```python
class ReportGenerator:
    @staticmethod
    def generate(phase_results: list[PhaseResult]) -> str:
        """Render complete audit report as markdown."""
        sections = []
        sections.append("# TelcoRetain Platform Audit Report\n")
        sections.append(f"**Generated:** {datetime.now().isoformat()}\n")

        # Executive Summary
        report = AuditReport(phases=phase_results, ...)
        sections.append(f"## Executive Summary\n")
        sections.append(f"- **Overall Score:** {report.weighted_score}/10")
        sections.append(f"- **Readiness:** {report.readiness}")
        sections.append(f"- **Critical Findings:** {report.total_critical}")
        sections.append(f"- **High Findings:** {report.total_high}")
        sections.append(f"- **Medium Findings:** {report.total_medium}\n")

        # Phase sections
        for phase in phase_results:
            sections.append(f"## Phase: {phase.phase_name}")
            sections.append(f"**Score: {phase.score}/10** ({phase.passed_checks}/{phase.total_checks} checks passed)\n")
            for finding in phase.findings:
                sections.append(f"### [{finding.severity.value}] {finding.title}")
                sections.append(f"{finding.description}")
                if finding.file_path:
                    sections.append(f"- **File:** `{finding.file_path}`")
                if finding.recommendation:
                    sections.append(f"- **Recommendation:** {finding.recommendation}")
                sections.append("")

        # Final Scorecard
        sections.append("## Final Scorecard\n")
        sections.append("| Phase | Score | Weight |")
        sections.append("|-------|-------|--------|")
        for phase in phase_results:
            w = weights.get(phase.phase_name, 1.0)
            sections.append(f"| {phase.phase_name} | {phase.score}/10 | {w}x |")

        # Remediation
        sections.append("\n## Prioritized Remediation\n")
        critical_findings = [f for pr in phase_results for f in pr.findings if f.severity == Severity.CRITICAL]
        high_findings = [f for pr in phase_results for f in pr.findings if f.severity == Severity.HIGH]
        for i, f in enumerate(critical_findings + high_findings, 1):
            sections.append(f"{i}. **[{f.severity.value}]** {f.title} — {f.recommendation}")

        return "\n".join(sections)
```

## Scoring Methodology

### Phase Score Calculation

```
Phase_Score = (passed_checks / total_checks) × 10
```

Each phase defines its own set of checks. A check either passes (no finding) or fails (produces a finding of Medium severity or higher).

### Weighted Overall Score

| Phase | Weight |
|-------|--------|
| Authentication Validation (Phase 9) | 1.5× |
| Security Testing (Phase 13) | 1.5× |
| Code Quality Review (Phase 14) | 0.75× |
| All other phases | 1.0× |

```
Weighted_Score = Σ(Phase_Score × Weight) / Σ(Weight)
```

### Readiness Classification

| Score Range | Classification |
|-------------|---------------|
| 8.0 – 10.0 | Production Ready |
| 6.0 – 7.9 | Production Ready with Caveats |
| 4.0 – 5.9 | Significant Rework Required |
| 0.0 – 3.9 | Not Production Ready |

## Error Handling

- **File not found:** Phase records finding with appropriate severity and continues
- **Parse errors:** AST parse failures are logged, file skipped with Medium finding
- **Runtime connection failure:** E2E and Performance phases report all checks as failed with explanatory note
- **Timeout:** Runtime checks use 10s timeout; exceeding timeout counts as failure
- **Severity filtering:** Only Medium, High, and Critical findings are included (Low is excluded per scope)

## Dependencies

**Python packages (audit tooling):**
- `ast` (stdlib) — Python AST parsing
- `pathlib` (stdlib) — File system navigation
- `re` (stdlib) — Regex pattern matching
- `httpx` — Async HTTP client for runtime verification
- `pandas` — CSV parsing for dataset validation
- `ruff` — Linting and dead code detection (CLI tool)

**External tools invoked:**
- `npx tsc --noEmit` — TypeScript type checking
- `pip-audit` — Python dependency vulnerability scanning
- `npm audit` — Node.js dependency vulnerability scanning

## Testing Strategy

### Unit Tests
- **Scoring logic:** Verify `PhaseResult.score` calculation with known inputs
- **Readiness classification:** Test all four threshold boundaries
- **Weighted calculation:** Test with varied phase scores and known weights
- **ReportGenerator:** Test markdown output contains required sections

### Property Tests (100+ iterations each)
- Properties 1–5, 6, 12–14: AST-based checks over generated file content
- Properties 7–8: Generated categorical values and feature columns
- Properties 9–10: Generated feature inputs through SHAP explainer
- Property 11: Generated customer profiles with varied ARPU/risk
- Properties 15–16: Generated score arrays with boundary testing

### Integration Tests
- End-to-end audit run on test fixture workspace (miniature project structure)
- Runtime phases against a test server instance
- Report generation from fixture findings

### Edge Cases
- Empty directories (0 files to count)
- Malformed Python files (AST parse failure)
- Missing ML artifacts directory
- Server unreachable for runtime phases
- All checks passing (perfect score)
- All checks failing (zero score)

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Layered Delegation — Routers to Services

For all API router files in `backend/app/api/v1/`, every endpoint function SHALL delegate business logic to an imported service class and SHALL NOT contain direct database queries or complex business logic inline.

**Validates: Requirements 3.1**

### Property 2: Repository Pattern Enforcement

For all service files in `backend/app/services/`, database operations SHALL be performed through imported repository class methods and SHALL NOT contain direct SQLAlchemy `session.execute()` or `session.query()` calls.

**Validates: Requirements 3.2**

### Property 3: Schema Validation Coverage

For all API endpoint functions that accept request bodies or return structured data, the endpoint SHALL declare a Pydantic model type annotation for the request parameter and a `response_model` for the response.

**Validates: Requirements 3.3, 13.1**

### Property 4: Async Session Safety

For all usages of `AsyncSessionLocal` across the codebase, the session SHALL be acquired via an `async with` context manager ensuring proper cleanup on both success and exception paths.

**Validates: Requirements 3.6**

### Property 5: List Endpoint Pagination

For all API endpoints that return a list of items (response type is a collection), the endpoint SHALL accept `limit` and `offset` (or `page` and `page_size`) query parameters to bound the result set.

**Validates: Requirements 3.7**

### Property 6: Foreign Key Cascade Definitions

For all `ForeignKey` column definitions in SQLAlchemy models, the column SHALL include an explicit `ondelete` cascade rule (e.g., CASCADE, SET NULL, RESTRICT).

**Validates: Requirements 4.3**

### Property 7: Categorical Encoding Completeness

For all unique categorical values present in the training dataset columns, the preprocessing encoder SHALL have a defined mapping, ensuring no unseen-category errors during inference.

**Validates: Requirements 5.2**

### Property 8: Null Handling Completeness

For all feature columns used in the ML pipeline, the preprocessing code SHALL include an explicit null-handling strategy (fillna, imputation, or dropna) rather than relying on implicit behavior.

**Validates: Requirements 5.5**

### Property 9: SHAP Additivity

For any valid feature input passed to the SHAP explainer, the sum of all SHAP values plus the expected base value SHALL equal the model's raw prediction output (within floating-point tolerance of ±0.01).

**Validates: Requirements 7.2**

### Property 10: Explanation Response Completeness

For any SHAP explanation response, every item in the explanation list SHALL contain a `feature_name` (string), `shap_value` (numeric), and a `direction` indicator (positive or negative contribution).

**Validates: Requirements 7.3**

### Property 11: Recommendation Personalization

For any customer with churn_probability < 0.3 and risk_category not equal to "HIGH", the recommendation engine SHALL NOT produce high-impact discount offers (expected_impact="HIGH"), and for any two customers with meaningfully different profiles (different ARPU tier or risk level), the generated offer sets SHALL differ.

**Validates: Requirements 8.3, 8.4**

### Property 12: RBAC Enforcement Coverage

For all API endpoint functions protected by authentication (using `Depends(get_current_user)`), the endpoint SHALL also include a role-based authorization check via `Depends(require_role(...))` with an explicit allowed-roles list.

**Validates: Requirements 10.2**

### Property 13: Documentation Coverage

For all public functions and classes (those not prefixed with `_`) in the backend codebase, the definition SHALL include a docstring providing at minimum a one-line description of purpose.

**Validates: Requirements 14.2**

### Property 14: Configuration Externalization

For all configuration values controlling runtime behavior (timeouts, rate limits, feature flags, retry counts), the value SHALL be sourced from environment variables or the Settings class rather than hardcoded as a literal in application code.

**Validates: Requirements 14.3**

### Property 15: Weighted Scorecard Calculation

For any set of 15 phase scores (each between 0 and 10), the weighted overall score SHALL equal the sum of (phase_score × weight) divided by the sum of weights, where Security and Authentication phases use weight 1.5 and Code Quality uses weight 0.75.

**Validates: Requirements 15.2**

### Property 16: Readiness Classification Correctness

For any weighted overall score, the readiness classification SHALL be "Production Ready" if score ≥ 8.0, "Production Ready with Caveats" if 6.0 ≤ score < 8.0, "Significant Rework Required" if 4.0 ≤ score < 6.0, and "Not Production Ready" if score < 4.0.

**Validates: Requirements 15.3**
