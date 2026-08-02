"""Celery Worker Configuration"""
from celery import Celery
from apex.config import settings

celery_app = Celery(
    "apex",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "apex.workers.tasks.scout_tasks",
        "apex.workers.tasks.analyst_tasks",
        "apex.workers.tasks.executor_tasks",
        "apex.workers.tasks.monetizer_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "apex.workers.tasks.scout_tasks.*": {"queue": "scout"},
        "apex.workers.tasks.analyst_tasks.*": {"queue": "analyst"},
        "apex.workers.tasks.executor_tasks.*": {"queue": "executor"},
        "apex.workers.tasks.monetizer_tasks.*": {"queue": "monetizer"},
    },
    beat_schedule={
        "apex-pipeline-cycle": {
            "task": "apex.workers.tasks.scout_tasks.run_scout_cycle",
            "schedule": 60.0,  # Every 60 seconds
        },
    },
)
