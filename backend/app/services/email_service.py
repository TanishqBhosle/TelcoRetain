"""
Email Service using SendGrid.
Handles email verification, password reset, and notification emails.
"""

from typing import Optional
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)


class EmailService:
    """SendGrid-based email service with graceful fallback."""

    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.from_email = settings.EMAIL_FROM
        self._client = None
        self._enabled = bool(self.api_key)

    def _get_client(self):
        """Lazy-load SendGrid client."""
        if self._client is None and self._enabled:
            try:
                from sendgrid import SendGridAPIClient
                self._client = SendGridAPIClient(api_key=self.api_key)
            except Exception as e:
                logger.warning("sendgrid_client_init_failed", error=str(e))
                self._enabled = False
        return self._client

    def is_enabled(self) -> bool:
        """Check if email service is configured and available."""
        return self._enabled

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email via SendGrid."""
        if not self._enabled:
            logger.info("email_service_disabled", to=to_email, subject=subject)
            return False

        client = self._get_client()
        if not client:
            return False

        try:
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            mail = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content),
            )
            if text_content:
                mail.content = [Content("text/plain", text_content), Content("text/html", html_content)]

            response = await client.send(mail)
            logger.info("email_sent", to=to_email, status=response.status_code)
            return response.status_code in (200, 202)
        except Exception as e:
            logger.error("email_send_failed", to=to_email, error=str(e))
            return False

    async def send_verification_email(self, email: str, token: str, frontend_url: str = "http://localhost:5173") -> bool:
        """Send email verification link."""
        verify_url = f"{frontend_url}/verify-email?token={token}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1d8a8a;">Welcome to Telco Retain!</h2>
                <p>Please verify your email address by clicking the link below:</p>
                <p><a href="{verify_url}" style="background: #1d8a8a; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Verify Email</a></p>
                <p>Or copy this link: {verify_url}</p>
                <p>This link expires in 24 hours.</p>
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #999;">If you didn't create an account, you can safely ignore this email.</p>
            </div>
        </body>
        </html>
        """
        
        text = f"Welcome to Telco Retain!\n\nVerify your email: {verify_url}\n\nThis link expires in 24 hours."
        
        return await self.send_email(email, "Verify your Telco Retain account", html, text)

    async def send_password_reset_email(self, email: str, token: str, frontend_url: str = "http://localhost:5173") -> bool:
        """Send password reset link."""
        reset_url = f"{frontend_url}/reset-password?token={token}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1d8a8a;">Password Reset Request</h2>
                <p>You requested a password reset. Click the link below to set a new password:</p>
                <p><a href="{reset_url}" style="background: #1d8a8a; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Password</a></p>
                <p>Or copy this link: {reset_url}</p>
                <p>This link expires in 15 minutes.</p>
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #999;">If you didn't request this, please ignore this email.</p>
            </div>
        </body>
        </html>
        """
        
        text = f"Password Reset Request\n\nReset your password: {reset_url}\n\nThis link expires in 15 minutes."
        
        return await self.send_email(email, "Reset your Telco Retain password", html, text)


# Singleton instance
email_service = EmailService()