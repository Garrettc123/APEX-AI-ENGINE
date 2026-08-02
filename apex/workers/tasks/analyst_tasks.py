from apex.workers.celery_app import celery_app

@celery_app.task(name="apex.workers.tasks.analyst_tasks.score_opportunity")
def score_opportunity(opportunity: dict) -> dict:
    import asyncio
    from apex.agents.analyst import AnalystAgent
    agent = AnalystAgent()
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(agent._score_opportunity(opportunity))
    loop.close()
    return result
