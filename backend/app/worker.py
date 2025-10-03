"""Celery worker configuration."""

from celery import Celery
import structlog

from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger(__name__)

# Create Celery app
celery_app = Celery(
    "garagereg",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.maintenance",
        "app.tasks.notifications",
        "app.tasks.reports",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


# Example tasks
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery."""
    logger.info("Debug task executed", task_id=self.request.id)
    return f"Debug task {self.request.id}"


@celery_app.task
def send_email_task(to: str, subject: str, body: str):
    """Send email task."""
    logger.info("Sending email", to=to, subject=subject)
    # TODO: Implement email sending
    return {"status": "sent", "to": to, "subject": subject}


@celery_app.task
def generate_maintenance_report_task(gate_id: int, period: str):
    """Generate maintenance report task."""
    logger.info("Generating maintenance report", gate_id=gate_id, period=period)
    # TODO: Implement report generation
    return {"status": "generated", "gate_id": gate_id, "period": period}


if __name__ == "__main__":
    celery_app.start()