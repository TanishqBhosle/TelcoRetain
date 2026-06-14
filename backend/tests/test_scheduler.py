"""Tests for scheduler module."""

import pytest
from unittest.mock import patch, MagicMock


class TestScheduler:
    """Tests for APScheduler setup."""

    def test_scheduler_import(self):
        from app.core.scheduler import scheduler, start_scheduler, shutdown_scheduler
        assert scheduler is not None

    def test_add_batch_prediction_job(self):
        from app.core.scheduler import add_batch_prediction_job, scheduler

        with patch.object(scheduler, "add_job") as mock_add:
            mock_add.return_value = MagicMock(id="test_job_1")
            job_id = add_batch_prediction_job(["cust1", "cust2"])
            mock_add.assert_called_once()

    def test_add_retraining_job(self):
        from app.core.scheduler import add_retraining_job, scheduler

        with patch.object(scheduler, "add_job") as mock_add:
            mock_add.return_value = MagicMock(id="retrain_1")
            job_id = add_retraining_job("v1.0")
            mock_add.assert_called_once()
