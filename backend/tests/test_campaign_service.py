"""Tests for campaign service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions.custom import NotFoundError


@pytest.mark.asyncio
class TestCampaignService:
    """Tests for CampaignService methods."""

    @patch("app.services.campaign_service.RecommendationRepository")
    @patch("app.services.campaign_service.CustomerRepository")
    @patch("app.services.campaign_service.CampaignRepository")
    async def test_create_campaign(self, mock_campaign_repo_cls, mock_customer_repo_cls, mock_rec_repo_cls):
        mock_campaign_repo = AsyncMock()
        mock_customer_repo = AsyncMock()
        mock_rec_repo = AsyncMock()

        mock_created = MagicMock()
        mock_created.id = uuid.uuid4()
        mock_created.name = "Test Campaign"
        mock_campaign_repo.create.return_value = mock_created

        from app.services.campaign_service import CampaignService
        from app.schemas.campaigns import CampaignCreate
        service = CampaignService(mock_campaign_repo, mock_customer_repo, mock_rec_repo)

        payload = CampaignCreate(
            name="Test Campaign",
            campaign_type="retention",
            start_date="2025-01-01",
            end_date="2025-02-01",
            is_active=True,
        )

        result = await service.create_campaign(uuid.uuid4(), payload)
        assert result.name == "Test Campaign"

    @patch("app.services.campaign_service.RecommendationRepository")
    @patch("app.services.campaign_service.CustomerRepository")
    @patch("app.services.campaign_service.CampaignRepository")
    async def test_get_campaign_not_found(self, mock_campaign_repo_cls, mock_customer_repo_cls, mock_rec_repo_cls):
        mock_campaign_repo = AsyncMock()
        mock_campaign_repo.get_by_id.return_value = None
        mock_customer_repo = AsyncMock()
        mock_rec_repo = AsyncMock()

        from app.services.campaign_service import CampaignService
        service = CampaignService(mock_campaign_repo, mock_customer_repo, mock_rec_repo)

        with pytest.raises(NotFoundError):
            await service.get_campaign(uuid.uuid4())

    @patch("app.services.campaign_service.RecommendationRepository")
    @patch("app.services.campaign_service.CustomerRepository")
    @patch("app.services.campaign_service.CampaignRepository")
    async def test_list_campaigns(self, mock_campaign_repo_cls, mock_customer_repo_cls, mock_rec_repo_cls):
        mock_campaign_repo = AsyncMock()
        mock_campaign_repo.list_campaigns.return_value = [MagicMock(), MagicMock()]
        mock_customer_repo = AsyncMock()
        mock_rec_repo = AsyncMock()

        from app.services.campaign_service import CampaignService
        service = CampaignService(mock_campaign_repo, mock_customer_repo, mock_rec_repo)

        result = await service.list_campaigns(page=1, limit=20)
        assert len(result) == 2
