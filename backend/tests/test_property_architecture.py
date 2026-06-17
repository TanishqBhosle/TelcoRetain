"""Property-based tests for Phase 3: Backend architectural pattern detection.

Uses hypothesis to generate synthetic Python code snippets representing
valid/invalid architectural patterns and verifies that the Phase 3
detection logic correctly identifies compliance and violations.

**Validates: Requirements 3.1, 3.2, 3.3, 3.6, 3.7**
"""

import ast
import textwrap

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from audit.phases.phase_03_backend import BackendValidationPhase


# ============================================================
# Shared Helpers
# ============================================================

phase = BackendValidationPhase()


def parse_code(code: str) -> ast.Module:
    """Parse a string of Python code into an AST module."""
    return ast.parse(textwrap.dedent(code))


# ============================================================
# Strategies for generating synthetic code patterns
# ============================================================

# Strategy: generate valid Python identifier names
identifier_st = st.from_regex(r"[a-z][a-z0-9_]{2,15}", fullmatch=True)

# Strategy: generate service class names
service_class_st = st.from_regex(r"[A-Z][a-z]{3,10}Service", fullmatch=True)

# Strategy: generate repository class names
repo_class_st = st.from_regex(r"[A-Z][a-z]{3,10}Repo(sitory)?", fullmatch=True)

# Strategy: HTTP methods for endpoint decorators
http_method_st = st.sampled_from(["get", "post", "put", "patch", "delete"])

# Strategy: session variable names that are detected
session_var_st = st.sampled_from(["session", "db", "sess"])

# Strategy: session methods that indicate direct DB usage
session_method_st = st.sampled_from(["execute", "query", "scalar", "scalars"])

# Strategy: broader session methods for service layer
service_session_method_st = st.sampled_from(
    ["execute", "query", "add", "commit", "rollback", "flush", "scalar", "scalars"]
)

# Strategy: pagination param pairs
pagination_pair_st = st.sampled_from([
    ("limit", "offset"),
    ("page", "page_size"),
    ("skip", "limit"),
])

# Strategy: Pydantic-like model names for response_model
schema_name_st = st.from_regex(r"[A-Z][a-z]{3,10}(Response|Schema|Out)", fullmatch=True)


# ============================================================
# Property 1: Layered Delegation — Routers to Services
# **Validates: Requirements 3.1**
# ============================================================

class TestProperty1LayeredDelegation:
    """Property 1: Layered Delegation — Routers to Services.

    For all API router files in backend/app/api/v1/, every endpoint
    function SHALL delegate business logic to an imported service class
    and SHALL NOT contain direct database queries or complex business
    logic inline.
    """

    @given(
        service_module=st.from_regex(r"app\.services\.[a-z_]{3,15}", fullmatch=True),
        service_class=service_class_st,
        func_name=identifier_st,
        method=http_method_st,
    )
    @settings(max_examples=100)
    def test_router_with_service_import_passes(
        self, service_module, service_class, func_name, method
    ):
        """A router that imports from services and delegates should pass."""
        code = f"""
from {service_module} import {service_class}

router = APIRouter()

@router.{method}("/items")
async def {func_name}():
    return await {service_class}().do_something()
"""
        module = parse_code(code)

        # Should detect service import
        from audit.utils.static_analyzer import StaticAnalyzer
        has_import = StaticAnalyzer.check_imports(module, "services")
        assert has_import, "Should detect service import"

        # Should NOT detect inline DB queries
        has_inline_db = phase._has_inline_db_queries(module)
        assert not has_inline_db, "Should not detect inline DB in delegating router"

    @given(
        func_name=identifier_st,
        method=http_method_st,
        session_var=session_var_st,
        session_method=session_method_st,
    )
    @settings(max_examples=100)
    def test_router_with_inline_db_fails(
        self, func_name, method, session_var, session_method
    ):
        """A router with direct DB queries should be flagged as violation."""
        code = f"""
router = APIRouter()

@router.{method}("/items")
async def {func_name}({session_var}):
    result = await {session_var}.{session_method}(something)
    return result
"""
        module = parse_code(code)

        # Should detect inline DB queries
        has_inline_db = phase._has_inline_db_queries(module)
        assert has_inline_db, (
            f"Should detect inline DB query: {session_var}.{session_method}()"
        )

    @given(
        func_name=identifier_st,
        method=http_method_st,
    )
    @settings(max_examples=100)
    def test_router_without_service_import_fails(self, func_name, method):
        """A router without service imports should be flagged."""
        code = f"""
from app.models.users import User

router = APIRouter()

@router.{method}("/items")
async def {func_name}():
    return {{"data": "inline logic"}}
"""
        module = parse_code(code)

        from audit.utils.static_analyzer import StaticAnalyzer
        has_import = StaticAnalyzer.check_imports(module, "services")
        assert not has_import, "Should NOT detect service import when none exists"


# ============================================================
# Property 2: Repository Pattern Enforcement
# **Validates: Requirements 3.2**
# ============================================================

class TestProperty2RepositoryPattern:
    """Property 2: Repository Pattern Enforcement.

    For all service files in backend/app/services/, database operations
    SHALL be performed through imported repository class methods and
    SHALL NOT contain direct SQLAlchemy session.execute() or
    session.query() calls.
    """

    @given(
        repo_module=st.from_regex(r"app\.repositories\.[a-z_]{3,15}", fullmatch=True),
        repo_class=repo_class_st,
        func_name=identifier_st,
    )
    @settings(max_examples=100)
    def test_service_with_repo_import_passes(
        self, repo_module, repo_class, func_name
    ):
        """A service that imports from repositories and uses them should pass."""
        code = f"""
from {repo_module} import {repo_class}

class SomeService:
    def __init__(self):
        self.repo = {repo_class}()

    async def {func_name}(self):
        return await self.repo.get_all()
"""
        module = parse_code(code)

        from audit.utils.static_analyzer import StaticAnalyzer
        has_import = StaticAnalyzer.check_imports(module, "repositories")
        assert has_import, "Should detect repository import"

        has_direct_session = phase._has_direct_session_usage(module)
        assert not has_direct_session, "Should not detect direct session usage"

    @given(
        func_name=identifier_st,
        session_var=session_var_st,
        session_method=service_session_method_st,
    )
    @settings(max_examples=100)
    def test_service_with_direct_session_fails(
        self, func_name, session_var, session_method
    ):
        """A service with direct session operations should be flagged."""
        code = f"""
class SomeService:
    async def {func_name}(self, {session_var}):
        result = await {session_var}.{session_method}(something)
        return result
"""
        module = parse_code(code)

        has_direct_session = phase._has_direct_session_usage(module)
        assert has_direct_session, (
            f"Should detect direct session usage: {session_var}.{session_method}()"
        )

    @given(
        func_name=identifier_st,
        session_method=service_session_method_st,
    )
    @settings(max_examples=100)
    def test_service_with_self_session_attr_fails(
        self, func_name, session_method
    ):
        """A service using self.session.method() should be flagged."""
        code = f"""
class SomeService:
    async def {func_name}(self):
        result = await self.session.{session_method}(something)
        return result
"""
        module = parse_code(code)

        has_direct_session = phase._has_direct_session_usage(module)
        assert has_direct_session, (
            f"Should detect self.session.{session_method}() usage"
        )


# ============================================================
# Property 3: Schema Validation Coverage
# **Validates: Requirements 3.3**
# ============================================================

class TestProperty3SchemaValidation:
    """Property 3: Schema Validation Coverage.

    For all API endpoint functions that accept request bodies or return
    structured data, the endpoint SHALL declare a Pydantic model type
    annotation for the request parameter and a response_model for
    the response.
    """

    @given(
        func_name=identifier_st,
        method=http_method_st,
        schema_name=schema_name_st,
    )
    @settings(max_examples=100)
    def test_endpoint_with_response_model_passes(
        self, func_name, method, schema_name
    ):
        """An endpoint with response_model should be detected as compliant."""
        code = f"""
from fastapi import APIRouter

router = APIRouter()

@router.{method}("/items", response_model={schema_name})
async def {func_name}():
    return {{}}
"""
        module = parse_code(code)
        endpoints = phase._find_endpoint_functions(module)
        assert len(endpoints) == 1, "Should find exactly one endpoint"

        has_response_model = phase._endpoint_has_response_model(module, endpoints[0])
        assert has_response_model, "Should detect response_model in decorator"

    @given(
        func_name=identifier_st,
        method=http_method_st,
    )
    @settings(max_examples=100)
    def test_endpoint_without_response_model_fails(self, func_name, method):
        """An endpoint without response_model should be flagged."""
        code = f"""
from fastapi import APIRouter

router = APIRouter()

@router.{method}("/items")
async def {func_name}():
    return {{}}
"""
        module = parse_code(code)
        endpoints = phase._find_endpoint_functions(module)
        assert len(endpoints) == 1, "Should find exactly one endpoint"

        has_response_model = phase._endpoint_has_response_model(module, endpoints[0])
        assert not has_response_model, "Should NOT detect response_model when absent"

    @given(
        func_name=identifier_st,
        method=http_method_st,
        schema_name=schema_name_st,
        path=st.from_regex(r"/[a-z]{3,10}", fullmatch=True),
    )
    @settings(max_examples=100)
    def test_endpoint_detection_with_various_paths(
        self, func_name, method, schema_name, path
    ):
        """Endpoint detection works regardless of the route path."""
        code = f"""
from fastapi import APIRouter

router = APIRouter()

@router.{method}("{path}", response_model={schema_name})
async def {func_name}():
    pass
"""
        module = parse_code(code)
        endpoints = phase._find_endpoint_functions(module)
        assert len(endpoints) == 1, f"Should detect endpoint for @router.{method}"


# ============================================================
# Property 4: Async Session Safety
# **Validates: Requirements 3.6**
# ============================================================

class TestProperty4AsyncSessionSafety:
    """Property 4: Async Session Safety.

    For all usages of AsyncSessionLocal across the codebase, the session
    SHALL be acquired via an async with context manager ensuring proper
    cleanup on both success and exception paths.
    """

    @given(
        func_name=identifier_st,
        var_name=st.from_regex(r"[a-z_]{3,10}", fullmatch=True),
    )
    @settings(max_examples=100)
    def test_safe_async_with_usage_passes(self, func_name, var_name):
        """AsyncSessionLocal inside async with should be detected as safe."""
        code = f"""
from app.core.database import AsyncSessionLocal

async def {func_name}():
    async with AsyncSessionLocal() as {var_name}:
        result = await {var_name}.execute(query)
    return result
"""
        module = parse_code(code)
        unsafe_lines = phase._find_unsafe_session_usage(module, None)
        assert len(unsafe_lines) == 0, "Should not flag safe async with usage"

    @given(
        func_name=identifier_st,
        var_name=st.from_regex(r"[a-z_]{3,10}", fullmatch=True),
    )
    @settings(max_examples=100)
    def test_unsafe_bare_call_fails(self, func_name, var_name):
        """AsyncSessionLocal() called without async with should be flagged."""
        code = f"""
from app.core.database import AsyncSessionLocal

async def {func_name}():
    {var_name} = AsyncSessionLocal()
    result = await {var_name}.execute(query)
    return result
"""
        module = parse_code(code)
        unsafe_lines = phase._find_unsafe_session_usage(module, None)
        assert len(unsafe_lines) > 0, (
            "Should flag AsyncSessionLocal() without async with"
        )

    @given(
        func_name=identifier_st,
    )
    @settings(max_examples=100)
    def test_multiple_safe_usages_all_pass(self, func_name):
        """Multiple async with usages in the same file should all pass."""
        code = f"""
from app.core.database import AsyncSessionLocal

async def {func_name}_1():
    async with AsyncSessionLocal() as session:
        return await session.execute(q1)

async def {func_name}_2():
    async with AsyncSessionLocal() as db:
        return await db.execute(q2)
"""
        module = parse_code(code)
        unsafe_lines = phase._find_unsafe_session_usage(module, None)
        assert len(unsafe_lines) == 0, "All async with usages should be safe"


# ============================================================
# Property 5: List Endpoint Pagination
# **Validates: Requirements 3.7**
# ============================================================

class TestProperty5ListEndpointPagination:
    """Property 5: List Endpoint Pagination.

    For all API endpoints that return a list of items, the endpoint SHALL
    accept limit and offset (or page and page_size) query parameters.
    """

    @given(
        func_name=identifier_st,
        method=st.sampled_from(["get"]),
        pagination_pair=pagination_pair_st,
        schema_name=schema_name_st,
    )
    @settings(max_examples=100)
    def test_list_endpoint_with_pagination_passes(
        self, func_name, method, pagination_pair, schema_name
    ):
        """A list endpoint with pagination params should pass detection."""
        param1, param2 = pagination_pair
        code = f"""
from typing import List
from fastapi import APIRouter

router = APIRouter()

@router.{method}("/items", response_model=List[{schema_name}])
async def {func_name}({param1}: int = 0, {param2}: int = 10):
    pass
"""
        module = parse_code(code)
        endpoints = phase._find_endpoint_functions(module)
        assert len(endpoints) == 1

        # Verify it's detected as a list return type
        returns_list = phase._returns_list_type(endpoints[0], module)
        assert returns_list, "Should detect List[] in response_model"

        # Verify pagination params are detected
        has_pagination = phase._has_pagination_params(endpoints[0])
        assert has_pagination, (
            f"Should detect pagination params: {param1}, {param2}"
        )

    @given(
        func_name=identifier_st,
        method=st.sampled_from(["get"]),
        schema_name=schema_name_st,
    )
    @settings(max_examples=100)
    def test_list_endpoint_without_pagination_fails(
        self, func_name, method, schema_name
    ):
        """A list endpoint without pagination should be flagged."""
        code = f"""
from typing import List
from fastapi import APIRouter

router = APIRouter()

@router.{method}("/items", response_model=List[{schema_name}])
async def {func_name}():
    pass
"""
        module = parse_code(code)
        endpoints = phase._find_endpoint_functions(module)
        assert len(endpoints) == 1

        returns_list = phase._returns_list_type(endpoints[0], module)
        assert returns_list, "Should detect List[] in response_model"

        has_pagination = phase._has_pagination_params(endpoints[0])
        assert not has_pagination, "Should NOT detect pagination when params are missing"

    @given(
        func_name=identifier_st,
        method=st.sampled_from(["get"]),
        schema_name=schema_name_st,
    )
    @settings(max_examples=100)
    def test_non_list_endpoint_not_flagged(self, func_name, method, schema_name):
        """Non-list endpoints should not be subject to pagination check."""
        code = f"""
from fastapi import APIRouter

router = APIRouter()

@router.{method}("/items/{{item_id}}", response_model={schema_name})
async def {func_name}(item_id: int):
    pass
"""
        module = parse_code(code)
        endpoints = phase._find_endpoint_functions(module)
        assert len(endpoints) == 1

        returns_list = phase._returns_list_type(endpoints[0], module)
        assert not returns_list, "Non-list response_model should not be flagged"

    @given(
        func_name=identifier_st,
        method=st.sampled_from(["get"]),
        schema_name=schema_name_st,
        pagination_pair=pagination_pair_st,
    )
    @settings(max_examples=100)
    def test_lowercase_list_annotation_detected(
        self, func_name, method, schema_name, pagination_pair
    ):
        """Python 3.9+ lowercase list[] in response_model should be detected."""
        param1, param2 = pagination_pair
        code = f"""
from fastapi import APIRouter

router = APIRouter()

@router.{method}("/items", response_model=list[{schema_name}])
async def {func_name}({param1}: int = 0, {param2}: int = 10):
    pass
"""
        module = parse_code(code)
        endpoints = phase._find_endpoint_functions(module)
        assert len(endpoints) == 1

        returns_list = phase._returns_list_type(endpoints[0], module)
        assert returns_list, "Should detect lowercase list[] in response_model"
