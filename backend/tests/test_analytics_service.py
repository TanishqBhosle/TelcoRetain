"""Tests for analytics service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
class TestAnalyticsService:
    """Tests for AnalyticsService methods."""

    @patch("app.services.analytics_service.CampaignRepository")
    async def test_get_dashboard_kpis(self, mock_campaign_repo_cls):
        mock_campaign_repo = AsyncMock()
        mock_campaign_repo.get_active_campaigns_count.return_value = 3

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 100
        mock_db.execute.return_value = mock_result

        from app.services.analytics_service import AnalyticsService
        service = AnalyticsService(mock_db, mock_campaign_repo)

        kpis = await service.get_dashboard_kpis()
        assert kpis is not None
        assert hasattr(kpis, "total_customers")

    @patch("app.services.analytics_service.CampaignRepository")
    async def test_get_churn_trends(self, mock_campaign_repo_cls):
        mock_campaign_repo = AsyncMock()
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        from app.services.analytics_service import AnalyticsService
        service = AnalyticsService(mock_db, mock_campaign_repo)

        trends = await service.get_churn_trends()
        assert trends is not None
