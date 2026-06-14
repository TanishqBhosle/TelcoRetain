"""APScheduler configuration for background jobs."""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

logger = logging.getLogger(__name__)

jobstores = {"default": MemoryJobStore()}
executors = {"default": ThreadPoolExecutor(max_workers=4)}
job_defaults = {"coalesce": True, "max_instances": 1}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
)


def start_scheduler():
    """Start the APScheduler instance."""
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started")


def shutdown_scheduler():
    """Shutdown the APScheduler instance."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler shut down")


def add_batch_prediction_job(customer_ids: list, job_id: str | None = None):
    """Enqueue a batch prediction job."""
    from app.services.prediction_service import _run_batch_prediction

    job = scheduler.add_job(
        _run_batch_prediction,
        "date",
        run_date=None,
        args=[customer_ids],
        id=job_id or f"batch_predict_{len(customer_ids)}",
        replace_existing=True,
    )
    logger.info(f"Batch prediction job scheduled: {job.id}")
    return job.id


def add_retraining_job(dataset_version_id: str | None = None, job_id: str | None = None):
    """Enqueue a model retraining job."""
    from app.services.model_service import _run_retraining

    job = scheduler.add_job(
        _run_retraining,
        "date",
        run_date=None,
        args=[dataset_version_id],
        id=job_id or "retrain_latest",
        replace_existing=True,
    )
    logger.info(f"Retraining job scheduled: {job.id}")
    return job.id
