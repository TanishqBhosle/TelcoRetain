"""Tests for email service."""

import pytest
from unittest.mock import patch, MagicMock


class TestEmailService:
    """Tests for EmailService methods."""

    def test_email_service_init(self):
        from app.services.email_service import EmailService
        service = EmailService()
        assert service is not None

    @patch("app.services.email_service.settings")
    def test_send_email_no_api_key(self, mock_settings):
        mock_settings.SENDGRID_API_KEY = None
        from app.services.email_service import EmailService
        service = EmailService()

        result = service.send_email("to@test.com", "Subject", "<p>Body</p>", "Body text")
        assert result is True  # gracefully skips when no API key

    def test_send_verification_email_no_api_key(self):
        from app.services.email_service import EmailService
        service = EmailService()
        with patch.object(service, "send_email", return_value=True) as mock_send:
            result = service.send_verification_email("to@test.com", "token123")
            mock_send.assert_called_once()
