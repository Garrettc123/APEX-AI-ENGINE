"""APEX Health & Integration Tests"""
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
    data = resp.json()
    assert "agents" in data
    assert len(data["agents"]) == 4


@pytest.mark.asyncio
async def test_revenue_snapshot():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/revenue/snapshot")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_revenue" in data


@pytest.mark.asyncio
async def test_subscription_tiers():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/subscriptions/tiers")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["tiers"]) == 3
    tier_ids = [t["id"] for t in data["tiers"]]
    assert "starter" in tier_ids
    assert "pro" in tier_ids
    assert "enterprise" in tier_ids


@pytest.mark.asyncio
async def test_scout_agent_discover():
    from apex.agents.scout import ScoutAgent
    agent = ScoutAgent()
    results = await agent.discover(cycle_id="test-001")
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.asyncio
async def test_analyst_mock_scoring():
    from apex.agents.analyst import AnalystAgent
    agent = AnalystAgent()
    opp = {"id": "test-001", "type": "real_estate", "source": "mock", "data": {"address": "123 Test"}}
    result = agent._mock_score(opp)
    assert 0 <= result["score"] <= 100
    assert "estimated_value" in result
    assert result["risk"] in ["low", "medium", "high"]


@pytest.mark.asyncio
async def test_full_pipeline_mock():
    from apex.core.orchestrator import ApexOrchestrator
    orch = ApexOrchestrator()
    await orch._execute_pipeline_cycle()
    assert orch.metrics.cycles_completed == 1
    assert orch.metrics.total_leads > 0
