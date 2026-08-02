"""Scout Worker Tasks"""
from apex.workers.celery_app import celery_app
import asyncio


@celery_app.task(name="apex.workers.tasks.scout_tasks.run_scout_cycle", bind=True, max_retries=3)
def run_scout_cycle(self):
    """Celery task: run full pipeline cycle"""
    try:
        from apex.core.orchestrator import ApexOrchestrator
        orch = ApexOrchestrator()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(orch._execute_pipeline_cycle())
        loop.close()
        return {"status": "completed"}
    except Exception as exc:
        self.retry(exc=exc, countdown=2 ** self.request.retries)
