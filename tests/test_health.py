"""APEX Health & Integration Tests — never assume mock leads or revenue."""
import pytest
from httpx import AsyncClient, ASGITransport
from apex.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "operational"
    assert data["engine"] == "APEX"


@pytest.mark.asyncio
async def test_agent_status_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/agents/status")
    assert resp.status_code == 200
    assert len(resp.json()["agents"]) == 4


@pytest.mark.asyncio
async def test_revenue_snapshot():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/revenue/snapshot")
    assert resp.status_code == 200
    assert "total_revenue" in resp.json()


@pytest.mark.asyncio
async def test_subscription_tiers():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/subscriptions/tiers")
    assert resp.status_code == 200
    tier_ids = [t["id"] for t in resp.json()["tiers"]]
    assert all(t in tier_ids for t in ("starter", "pro", "enterprise"))


@pytest.mark.asyncio
async def test_scout_agent_discover():
    from apex.agents.scout import ScoutAgent
    results = await ScoutAgent().discover(cycle_id="test-source-backed")
    assert isinstance(results, list)
    assert all(x["source"] == "public_listing_verified_research" for x in results)
    assert all(x["authorized_for_outreach"] is False for x in results)


@pytest.mark.asyncio
async def test_analyst_no_simulated_valuation():
    from apex.agents.analyst import AnalystAgent
    opp = {"id": "test-research-only", "type": "real_estate", "source": "public_listing_verified_research",
           "research_only": True, "data": {"address": "Cleburne", "asking_price_usd": 100}}
    result = await AnalystAgent()._score_opportunity(opp)
    assert result["score"] == 0
    assert result["estimated_value"] is None
    assert result["authorized_for_outreach"] is False


@pytest.mark.asyncio
async def test_executor_no_unapproved_actions():
    from apex.agents.executor import ExecutorAgent
    result = await ExecutorAgent().execute([{"opportunity": {"id": "test"},
                                            "action": "send_proposal", "score": 99}], "test")
    assert result[0]["ready_to_invoice"] is False
    assert result[0]["result"]["outbound_sent"] is False


@pytest.mark.asyncio
async def test_monetizer_zero_without_settlement():
    from apex.agents.monetizer import MonetizerAgent
    agent = MonetizerAgent()
    assert await agent.monetize([{"ready_to_invoice": True,
                                 "estimated_value": 999999}], "test") == 0
    with pytest.raises(PermissionError):
        await agent.create_subscription("test", "test")


@pytest.mark.asyncio
async def test_full_pipeline_research_only():
    from apex.core.orchestrator import ApexOrchestrator
    orch = ApexOrchestrator()
    await orch._execute_pipeline_cycle()
    assert orch.metrics.cycles_completed == 1
    assert orch.metrics.total_leads >= 0
    assert orch.metrics.total_revenue == 0
    assert orch.metrics.deals_closed == 0
