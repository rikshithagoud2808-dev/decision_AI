import json
import logging
from typing import Dict, Any
from app.agents.llm_client import LLMClient

logger = logging.getLogger("decision_ai.critic")

class DecisionCritic:
    """
    Agent 3: Decision Critic (Adversarial Agent / Devil's Advocate)
    Challenges the optimistic assumptions of both paths, highlights hidden risks,
    exposes market realities, evaluates cognitive overload, and provides stress tests.
    """
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def critique(self, analysis: Dict[str, Any], simulation: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        dilemma = user_data.get("dilemma", "")
        hours_per_week = user_data.get("hours_per_week", 15)
        path_a = simulation.get("path_a", {})
        path_b = simulation.get("path_b", {})

        system_instruction = """
You are the "Decision Critic" Agent in a Multi-Agent Life Decision Simulation System.
Your job is to be the honest, skeptical, and rigorous devil's advocate.
Most students underestimate:
1. Prerequisite knowledge required
2. Time needed to debug and deploy
3. The brutality of entry-level hiring filters
4. Burnout risk when balancing college coursework with self-study

Critique BOTH Path A and Path B. Uncover blind spots, rate the burnout risk, and offer concrete mitigation steps.

Return JSON in this exact structure:
{
  "path_a_critique": {
    "blind_spots": ["Blind spot 1", "Blind spot 2"],
    "market_reality_check": "Realistic assessment of hiring competition and barriers",
    "burnout_risk_score": 7,
    "failure_mode": "The most likely scenario where this path fails or stalls",
    "mitigation_strategy": "How to de-risk this path if chosen"
  },
  "path_b_critique": {
    "blind_spots": ["Blind spot 1", "Blind spot 2"],
    "market_reality_check": "Realistic assessment of hiring competition and barriers",
    "burnout_risk_score": 5,
    "failure_mode": "The most likely scenario where this path fails or stalls",
    "mitigation_strategy": "How to de-risk this path if chosen"
  },
  "critical_tradeoff_verdict": "A concise paragraph summarizing the ultimate clash between the two options."
}
"""

        user_input_prompt = f"""
Decision Dilemma: {dilemma}
User Available Time: {hours_per_week} hours/week
Baseline: {analysis.get('current_level')}

Path A Simulated:
Title: {path_a.get('title')}
Required Hours: {path_a.get('weekly_effort_hours')}
Difficulties: {path_a.get('expected_difficulties')}

Path B Simulated:
Title: {path_b.get('title')}
Required Hours: {path_b.get('weekly_effort_hours')}
Difficulties: {path_b.get('expected_difficulties')}
"""

        result = self.llm.generate_json(system_instruction, user_input_prompt)
        if result and "path_a_critique" in result and "path_b_critique" in result:
            logger.info("Decision Critic completed using LLM.")
            return result

        logger.info("Using heuristic simulation engine for Decision Critic.")
        return self._heuristic_critique(analysis, simulation, user_data)

    def _heuristic_critique(self, analysis: Dict[str, Any], simulation: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        hours = int(data.get("hours_per_week", 15))
        dilemma_lower = data.get("dilemma", "").lower()

        if "ai" in dilemma_lower or "python" in dilemma_lower or "web" in dilemma_lower:
            return {
                "path_a_critique": {
                    "blind_spots": [
                        "Underestimating foundational mathematics (linear algebra, vector embeddings, loss functions) which makes debugging model failures frustrating.",
                        "Building standard tutorial wrapper projects (e.g. basic Chatbot with OpenAI key) that do not impress recruiters.",
                        f"At {hours} hours/week, 6 months leaves minimal room to both understand deep learning theory and build enterprise-grade apps."
                    ],
                    "market_reality_check": "Most high-paying AI/ML engineer roles demand previous production experience or advanced degrees. Fresh graduates who succeed in AI usually win by open-source contributions or by packaging AI models into full-stack web products.",
                    "burnout_risk_score": 8,
                    "failure_mode": "Getting stuck in 'tutorial purgatory'—watching theory videos without completing a distinctive, functioning end-to-end deployed project.",
                    "mitigation_strategy": "Do not treat AI in isolation. Combine Python AI logic with lightweight FastAPI endpoints and interactive frontends (Streamlit/React) so recruiters can test your work live."
                },
                "path_b_critique": {
                    "blind_spots": [
                        "High saturation at the beginner level: thousands of bootcamp grads build the same Todo app and clone portfolios.",
                        "Frontend toolchain churn: wasting time switching between bundlers, frameworks, and UI libraries rather than mastering core JavaScript & network protocols.",
                        "Neglecting backend fundamentals like database indexing, query optimization, and secure session management."
                    ],
                    "market_reality_check": "While junior web dev has massive openings, applicant volume per job posting is 3x to 5x higher. Clean UI/UX, responsive mobile design, and live deployed URLs are mandatory table-stakes to pass initial screening.",
                    "burnout_risk_score": 5,
                    "failure_mode": "Building generic clones (Netflix/Spotify UI clones) that showcase zero business logic or API data architecture.",
                    "mitigation_strategy": "Build one domain-specific business application (e.g., medical clinic booking or student exam portal) with authentication, database relationships, and automated tests."
                },
                "critical_tradeoff_verdict": "Path A offers higher long-term career upside and intellectual prestige, but carries high execution risk and a steeper barrier to entry for early internships. Path B has a much faster time-to-market and higher volume of entry roles, but requires superior polish to stand out against high candidate saturation."
            }

        return {
            "path_a_critique": {
                "blind_spots": [
                    "Underestimating the steep ramp-up time before seeing tangible returns.",
                    "Assuming academic prestige automatically translates to immediate hiring offers."
                ],
                "market_reality_check": "High specialization commands respect, but opportunities are narrower and hiring cycles are longer.",
                "burnout_risk_score": 7,
                "failure_mode": "Losing momentum mid-way due to delayed feedback loops.",
                "mitigation_strategy": "Create modular milestone checkpoints every 30 days to measure progress tangibly."
            },
            "path_b_critique": {
                "blind_spots": [
                    "Overemphasizing immediate wins while potentially neglecting long-term architectural depth.",
                    "Higher commoditization risk if projects remain surface-level."
                ],
                "market_reality_check": "Readily accessible opportunities, but requires proactive personal branding to stand out.",
                "burnout_risk_score": 5,
                "failure_mode": "Settling into low-difficulty execution that fails to demonstrate senior potential.",
                "mitigation_strategy": "Incorporate non-trivial engineering challenges (caching, security, scaling) into your builds."
            },
            "critical_tradeoff_verdict": "Path A favors patient, high-conviction specialization, whereas Path B maximizes immediate market liquidity and execution velocity."
        }

