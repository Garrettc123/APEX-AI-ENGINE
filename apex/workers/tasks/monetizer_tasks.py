from apex.workers.celery_app import celery_app

@celery_app.task(name="apex.workers.tasks.monetizer_tasks.process_payment")
def process_payment(action: dict) -> float:
    import asyncio
    from apex.agents.monetizer import MonetizerAgent
    agent = MonetizerAgent()
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(agent._process_payment(action))
    loop.close()
    return result
