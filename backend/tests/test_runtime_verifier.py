"""Tests for the RuntimeVerifier utility.

Tests use httpx's built-in MockTransport to simulate HTTP responses
without requiring a real server or external mocking libraries.
"""

import pytest
import httpx

from audit.utils.runtime_verifier import RuntimeVerifier


def _mock_transport(handler):
    """Create an httpx MockTransport from a handler function."""
    return httpx.MockTransport(handler)


def _health_ok_handler(request: httpx.Request) -> httpx.Response:
    """Mock handler that returns 200 for /health."""
    if request.url.path == "/health":
        return httpx.Response(200, json={"status": "ok"})
    return httpx.Response(404)


def _health_down_handler(request: httpx.Request) -> httpx.Response:
    """Mock handler that returns 503 for /health."""
    if request.url.path == "/health":
        return httpx.Response(503, json={"status": "unavailable"})
    return httpx.Response(404)


def _multi_endpoint_handler(request: httpx.Request) -> httpx.Response:
    """Mock handler supporting multiple endpoints."""
    if request.url.path == "/health":
        return httpx.Response(200, json={"status": "ok"})
    elif request.url.path == "/api/v1/customers":
        return httpx.Response(200, json={"customers": []})
    elif request.url.path == "/api/v1/predictions":
        return httpx.Response(201, json={"prediction_id": "abc123"})
    elif request.url.path == "/api/v1/error":
        return httpx.Response(500, text="Internal Server Error")
    return httpx.Response(404)


class TestRuntimeVerifierInit:
    """Tests for RuntimeVerifier initialization."""

    def test_default_base_url(self):
        verifier = RuntimeVerifier()
        assert verifier.base_url == "http://localhost:8000"

    def test_custom_base_url(self):
        verifier = RuntimeVerifier("http://example.com:9000")
        assert verifier.base_url == "http://example.com:9000"

    def test_client_is_none_before_entry(self):
        verifier = RuntimeVerifier()
        assert verifier.client is None


class TestRuntimeVerifierContextManager:
    """Tests for async context manager behavior."""

    @pytest.mark.asyncio
    async def test_client_created_on_entry(self):
        async with RuntimeVerifier() as verifier:
            assert verifier.client is not None
            assert isinstance(verifier.client, httpx.AsyncClient)

    @pytest.mark.asyncio
    async def test_client_closed_on_exit(self):
        verifier = RuntimeVerifier()
        async with verifier:
            assert verifier.client is not None
        assert verifier.client is None

    @pytest.mark.asyncio
    async def test_returns_self_on_entry(self):
        verifier = RuntimeVerifier()
        result = await verifier.__aenter__()
        assert result is verifier
        await verifier.__aexit__(None, None, None)


class TestCheckHealth:
    """Tests for check_health method."""

    @pytest.mark.asyncio
    async def test_returns_true_when_server_healthy(self):
        verifier = RuntimeVerifier("http://testserver")
        verifier.client = httpx.AsyncClient(
            transport=_mock_transport(_health_ok_handler),
            base_url="http://testserver",
        )
        try:
            result = await verifier.check_health()
            assert result is True
        finally:
            await verifier.client.aclose()

    @pytest.mark.asyncio
    async def test_returns_false_when_server_unhealthy(self):
        verifier = RuntimeVerifier("http://testserver")
        verifier.client = httpx.AsyncClient(
            transport=_mock_transport(_health_down_handler),
            base_url="http://testserver",
        )
        try:
            result = await verifier.check_health()
            assert result is False
        finally:
            await verifier.client.aclose()

    @pytest.mark.asyncio
    async def test_returns_false_on_connection_error(self):
        def raise_error(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Connection refused")

        verifier = RuntimeVerifier("http://testserver")
        verifier.client = httpx.AsyncClient(
            transport=_mock_transport(raise_error),
            base_url="http://testserver",
        )
        try:
            result = await verifier.check_health()
            assert result is False
        finally:
            await verifier.client.aclose()

    @pytest.mark.asyncio
    async def test_raises_runtime_error_without_context(self):
        verifier = RuntimeVerifier()
        with pytest.raises(RuntimeError, match="async context manager"):
            await verifier.check_health()


class TestMeasureResponseTime:
    """Tests for measure_response_time method."""

    @pytest.mark.asyncio
    async def test_returns_elapsed_and_status_code(self):
        verifier = RuntimeVerifier("http://testserver")
        verifier.client = httpx.AsyncClient(
            transport=_mock_transport(_multi_endpoint_handler),
            base_url="http://testserver",
        )
        try:
            elapsed, status = await verifier.measure_response_time("GET", "/health")
            assert isinstance(elapsed, float)
            assert elapsed >= 0.0
            assert status == 200
        finally:
            await verifier.client.aclose()

    @pytest.mark.asyncio
    async def test_get_request(self):
        verifier = RuntimeVerifier("http://testserver")
        verifier.client = httpx.AsyncClient(
            transport=_mock_transport(_multi_endpoint_handler),
            base_url="http://testserver",
        )
        try:
            elapsed, status = await verifier.measure_response_time(
                "GET", "/api/v1/customers"
            )
            assert status == 200
            assert elapsed >= 0.0
        finally:
            await verifier.client.aclose()

    @pytest.mark.asyncio
    async def test_post_request(self):
        verifier = RuntimeVerifier("http://testserver")
        verifier.client = httpx.AsyncClient(
            transport=_mock_transport(_multi_endpoint_handler),
            base_url="http://testserver",
        )
        try:
            elapsed, status = await verifier.measure_response_time(
                "POST", "/api/v1/predictions", json={"customer_id": "123"}
            )
            assert status == 201
            assert elapsed >= 0.0
        finally:
            await verifier.client.aclose()

    @pytest.mark.asyncio
    async def test_server_error_response(self):
        verifier = RuntimeVerifier("http://testserver")
        verifier.client = httpx.AsyncClient(
            transport=_mock_transport(_multi_endpoint_handler),
            base_url="http://testserver",
        )
        try:
            elapsed, status = await verifier.measure_response_time(
                "GET", "/api/v1/error"
            )
            assert status == 500
            assert elapsed >= 0.0
        finally:
            await verifier.client.aclose()

    @pytest.mark.asyncio
    async def test_not_found_response(self):
        verifier = RuntimeVerifier("http://testserver")
        verifier.client = httpx.AsyncClient(
            transport=_mock_transport(_multi_endpoint_handler),
            base_url="http://testserver",
        )
        try:
            elapsed, status = await verifier.measure_response_time(
                "GET", "/nonexistent"
            )
            assert status == 404
            assert elapsed >= 0.0
        finally:
            await verifier.client.aclose()

    @pytest.mark.asyncio
    async def test_raises_runtime_error_without_context(self):
        verifier = RuntimeVerifier()
        with pytest.raises(RuntimeError, match="async context manager"):
            await verifier.measure_response_time("GET", "/health")

    @pytest.mark.asyncio
    async def test_kwargs_passed_to_request(self):
        """Verify that additional kwargs are forwarded to the HTTP client."""
        received_headers = {}

        def capture_handler(request: httpx.Request) -> httpx.Response:
            received_headers.update(dict(request.headers))
            return httpx.Response(200)

        verifier = RuntimeVerifier("http://testserver")
        verifier.client = httpx.AsyncClient(
            transport=_mock_transport(capture_handler),
            base_url="http://testserver",
        )
        try:
            await verifier.measure_response_time(
                "GET", "/test", headers={"X-Custom": "audit"}
            )
            assert received_headers.get("x-custom") == "audit"
        finally:
            await verifier.client.aclose()
