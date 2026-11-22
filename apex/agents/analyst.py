"""Analyst Agent — research-scoring suggestions, never cash or sale evidence."""
from typing import List, Dict, Any
import structlog
from apex.agents.base_agent import BaseAgent
from apex.config import settings

log = structlog.get_logger()


def unverified_assessment(opp: Dict, reason: str) -> Dict:
    """Fail closed when a verifiable assessment cannot be produced."""
    return {
        "score": 0,
        "risk": "unverified",
        "estimated_value": None,
        "action": "research_only",
        "rationale": reason,
        "opportunity": opp,
        "buyer_committed": False,
        "profit_verified": False,
        "authorized_for_outreach": False,
    }


class AnalystAgent(BaseAgent):
    SCORE_THRESHOLD = 60

    def __init__(self):
        super().__init__(name="AnalystAgent")

    async def qualify(self, opportunities: List[Dict], cycle_id: str) -> List[Dict]:
        await self._set_running()
        qualified = []
        try:
            for opp in opportunities:
                try:
                    scored = await self._score_opportunity(opp)
                    if scored["score"] >= self.SCORE_THRESHOLD:
                        qualified.append(scored)
                        self.log.info("analyst.qualified", id=opp.get("id"), score=scored["score"])
                    else:
                        self.log.info("analyst.research_only", id=opp.get("id"), score=scored["score"])
                except Exception as exc:
                    self.log.error("analyst.score_error", id=opp.get("id"), error=type(exc).__name__)
        finally:
            await self._set_idle()
        return qualified

    async def _score_opportunity(self, opp: Dict) -> Dict:
        if opp.get("type") == "real_estate":
            return unverified_assessment(
                opp,
                "Public listing and buyer criteria match only. No seller contract, appraisal, buyer commitment or legal review; keep research-only.",
            )
        if not settings.OPENAI_API_KEY:
            return unverified_assessment(opp, "No configured assessment provider. No synthetic scores or estimated earnings.")
        try:
            from openai import AsyncOpenAI
            import json
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content":
                    "Evaluate the attached business opportunity with explicit uncertainty. "
                    "Return only JSON with score integer 0-100, risk, rationale. "
                    "Never invent revenue, payment or buyer acceptance. Opportunity: " + json.dumps(opp)}],
                response_format={"type": "json_object"},
                max_tokens=300,
            )
            result = json.loads(response.choices[0].message.content)
            score = result.get("score")
            if type(score) is not int or not 0 <= score <= 100:
                return unverified_assessment(opp, "Invalid model assessment; discarded.")
            return {
                "score": score,
                "risk": str(result.get("risk") or "unverified")[:32],
                "estimated_value": None,  # Do not turn model conjecture into cash projections
                "action": "research_only",
                "rationale": str(result.get("rationale") or "Model heuristic only; evidence review required.")[:500],
                "opportunity": opp,
                "buyer_committed": False,
                "profit_verified": False,
                "authorized_for_outreach": False,
            }
        except Exception as exc:
            self.log.warning("analyst.provider_unavailable", error=type(exc).__name__)
            return unverified_assessment(opp, "Assessment provider unavailable. No synthetic fallback.")
