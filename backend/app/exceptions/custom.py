"""
Custom platform exceptions.
"""

from typing import Any, Optional


class PlatformException(Exception):
    """Base exception for all platform errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        data: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.data = data


class AuthenticationError(PlatformException):
    """Raised when authentication credentials fail or are missing."""

    def __init__(self, message: str = "Authentication failed", data: Optional[Any] = None) -> None:
        super().__init__(message, status_code=401, data=data)


class AuthorizationError(PlatformException):
    """Raised when the user lacks the necessary permission/role."""

    def __init__(self, message: str = "Not authorized to access this resource", data: Optional[Any] = None) -> None:
        super().__init__(message, status_code=403, data=data)


class NotFoundError(PlatformException):
    """Generic not found error."""

    def __init__(self, message: str = "Resource not found", data: Optional[Any] = None) -> None:
        super().__init__(message, status_code=404, data=data)


class CustomerNotFoundError(NotFoundError):
    """Raised when a specific telecom customer ID is not found."""

    def __init__(self, customer_id: Any) -> None:
        super().__init__(f"Customer with ID '{customer_id}' not found")


class CampaignNotFoundError(NotFoundError):
    """Raised when a campaign is not found."""

    def __init__(self, campaign_id: Any) -> None:
        super().__init__(f"Campaign with ID '{campaign_id}' not found")


class ModelNotFoundError(NotFoundError):
    """Raised when an ML model is not found."""

    def __init__(self, model_id: Any) -> None:
        super().__init__(f"ML Model with ID '{model_id}' not found")


class DatasetNotFoundError(NotFoundError):
    """Raised when a dataset is not found."""

    def __init__(self, dataset_id: Any) -> None:
        super().__init__(f"Dataset with ID '{dataset_id}' not found")


class ValidationError(PlatformException):
    """Raised when validation check fails."""

    def __init__(self, message: str = "Validation failed", data: Optional[Any] = None) -> None:
        super().__init__(message, status_code=422, data=data)


class ConflictError(PlatformException):
    """Raised when there is a state conflict (e.g. duplicate email)."""

    def __init__(self, message: str = "Resource already exists", data: Optional[Any] = None) -> None:
        super().__init__(message, status_code=409, data=data)


class ModelNotLoadedError(PlatformException):
    """Raised when attempting inference but models are not initialized."""

    def __init__(self, message: str = "ML model registry is not loaded or configured") -> None:
        super().__init__(message, status_code=503)
