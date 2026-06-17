"""Runtime verification utilities for audit phases requiring live server interaction.

Provides an async HTTP client wrapper for measuring endpoint response
times and verifying server health during audit execution.
"""

import time
from typing import Optional

import httpx


class RuntimeVerifier:
    """Async HTTP client for runtime verification of API endpoints.

    Designed to be used as an async context manager. Wraps httpx.AsyncClient
    with utilities for measuring response times and checking server health.

    Attributes:
        base_url: The base URL of the server to verify.
        client: The underlying httpx.AsyncClient instance (set on entry).

    Example:
        async with RuntimeVerifier("http://localhost:8000") as verifier:
            if await verifier.check_health():
                elapsed, status = await verifier.measure_response_time("GET", "/api/v1/customers")
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the RuntimeVerifier.

        Args:
            base_url: Base URL of the server to verify. Defaults to
                http://localhost:8000.
        """
        self.base_url = base_url
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "RuntimeVerifier":
        """Enter the async context, creating the HTTP client.

        Returns:
            The RuntimeVerifier instance with an active client.
        """
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)
        return self

    async def __aexit__(self, *args) -> None:
        """Exit the async context, closing the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None

    async def measure_response_time(
        self, method: str, path: str, **kwargs
    ) -> tuple[float, int]:
        """Measure the response time of an HTTP request.

        Sends an HTTP request using the specified method and path, timing
        the duration from request initiation to response receipt.

        Args:
            method: HTTP method (e.g. "GET", "POST", "PUT", "DELETE").
            path: URL path relative to the base URL (e.g. "/health").
            **kwargs: Additional keyword arguments passed to
                httpx.AsyncClient.request (e.g. json, headers, params).

        Returns:
            A tuple of (elapsed_seconds, status_code) where elapsed_seconds
            is the wall-clock time for the request and status_code is the
            HTTP response status code.

        Raises:
            RuntimeError: If called outside of an async context manager.
            httpx.HTTPError: If the request fails due to network issues.
        """
        if self.client is None:
            raise RuntimeError(
                "RuntimeVerifier must be used as an async context manager."
            )

        start = time.perf_counter()
        response = await self.client.request(method, path, **kwargs)
        elapsed = time.perf_counter() - start
        return elapsed, response.status_code

    async def check_health(self) -> bool:
        """Verify that the server is running and responding.

        Sends a GET request to the /health endpoint and checks for
        a 200 status code. Any exception (connection refused, timeout,
        etc.) is treated as the server being unavailable.

        Returns:
            True if the server responds with HTTP 200, False otherwise.

        Raises:
            RuntimeError: If called outside of an async context manager.
        """
        if self.client is None:
            raise RuntimeError(
                "RuntimeVerifier must be used as an async context manager."
            )

        try:
            resp = await self.client.get("/health")
            return resp.status_code == 200
        except Exception:
            return False
