from apex.workers.celery_app import celery_app

@celery_app.task(name="apex.workers.tasks.executor_tasks.process_lead")
def process_lead(lead: dict, cycle_id: str) -> dict:
    import asyncio
    from apex.agents.executor import ExecutorAgent
    agent = ExecutorAgent()
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(agent._process_lead(lead, cycle_id))
    loop.close()
    return result
