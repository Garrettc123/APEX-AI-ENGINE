"""Analyst Agent — AI-powered qualification and scoring"""
from typing import List, Dict, Any
import structlog

from apex.agents.base_agent import BaseAgent
from apex.config import settings

log = structlog.get_logger()


class AnalystAgent(BaseAgent):
    """
    The Analyst Agent uses GPT-4o to:
    - Score each opportunity 0-100
    - Assess risk profile
    - Estimate deal value
    - Filter out low-quality leads
    - Generate action recommendation
    """

    SCORE_THRESHOLD = 60  # Only pass leads scoring >= 60

    def __init__(self):
        super().__init__(name="AnalystAgent")

    async def qualify(self, opportunities: List[Dict], cycle_id: str) -> List[Dict]:
        await self._set_running()
        qualified = []

        for opp in opportunities:
            try:
                scored = await self._score_opportunity(opp)
                if scored["score"] >= self.SCORE_THRESHOLD:
                    qualified.append(scored)
                    self.log.info("analyst.qualified", id=opp["id"], score=scored["score"])
                else:
                    self.log.info("analyst.rejected", id=opp["id"], score=scored["score"])
            except Exception as e:
                self.log.error("analyst.score_error", id=opp.get("id"), error=str(e))

        await self._set_idle()
        return qualified

    async def _score_opportunity(self, opp: Dict) -> Dict:
        """Use GPT-4o to intelligently score and qualify the opportunity"""
        if not settings.OPENAI_API_KEY:
            return self._mock_score(opp)

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

            prompt = f"""You are an expert business analyst for Garcar Enterprise.

Analyze this opportunity and return a JSON response:
{opp}

Return ONLY valid JSON with these fields:
- score: integer 0-100 (overall quality)
- risk: string (low/medium/high)
- estimated_value: float (dollar amount)
- action: string (what to do)
- rationale: string (brief explanation)"""

            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=300,
            )
            import json
            result = json.loads(response.choices[0].message.content)
            result["opportunity"] = opp
            return result
        except Exception as e:
            self.log.warning("analyst.openai_fallback", error=str(e))
            return self._mock_score(opp)

    def _mock_score(self, opp: Dict) -> Dict:
        """Fallback scoring when OpenAI unavailable"""
        import random
        score = random.randint(55, 95)
        return {
            "score": score,
            "risk": "medium" if score < 75 else "low",
            "estimated_value": round(random.uniform(500, 50000), 2),
            "action": "contact_seller" if opp["type"] == "real_estate" else "send_proposal",
            "rationale": "Automated scoring (OpenAI not configured)",
            "opportunity": opp,
        }
