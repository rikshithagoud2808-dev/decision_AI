import json
import logging
from typing import Dict, Any
from app.agents.llm_client import LLMClient

logger = logging.getLogger("decision_ai.analyzer")

class SituationAnalyzer:
    """
    Agent 1: Situation Analyzer
    Dissects user input, extracts implicit & explicit constraints, identifies
    competing options (Path A vs Path B), and isolates key success factors.
    """
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def analyze(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = user_data.get("dilemma", "")
        timeframe = user_data.get("timeframe", "6 months")
        hours_per_week = user_data.get("hours_per_week", 15)
        current_skills = user_data.get("current_skills", "Beginner / Some coding knowledge")
        primary_goal = user_data.get("primary_goal", "Job / Internship Readiness")
        risk_tolerance = user_data.get("risk_tolerance", "Moderate")

        system_instruction = """
You are the "Situation Analyzer" Agent in a Multi-Agent Life Decision Simulation System.
Your job is to deeply understand a user's dilemma and profile, then break it down into a structured foundation.

Identify:
1. Two distinct competing paths (Path A and Path B) representing the core choices.
2. The core trade-off or conflict between these paths.
3. User constraints (timeframe, weekly hours, current baseline).
4. Critical success factors required to succeed in either path.

Return JSON in this exact structure:
{
  "summary": "Brief 2-sentence summary of the decision context",
  "path_a_label": "Short descriptive title for Path A",
  "path_b_label": "Short descriptive title for Path B",
  "core_conflict": "The fundamental tension between the two options",
  "timeline_months": 6,
  "hours_per_week": 15,
  "current_level": "Assessed skill level",
  "target_milestone": "The primary outcome sought",
  "key_constraints": ["Constraint 1", "Constraint 2", "Constraint 3"],
  "key_success_factors": ["Factor 1", "Factor 2", "Factor 3"]
}
"""

        user_input_prompt = f"""
Decision Dilemma: {prompt}
Timeframe Available: {timeframe}
Hours Per Week: {hours_per_week}
Current Skills / Background: {current_skills}
Primary Goal: {primary_goal}
Risk Tolerance: {risk_tolerance}
"""

        result = self.llm.generate_json(system_instruction, user_input_prompt)
        if result and "path_a_label" in result and "path_b_label" in result:
            logger.info("Situation Analyzer completed using LLM.")
            return result

        logger.info("Using heuristic simulation engine for Situation Analyzer.")
        return self._heuristic_analysis(user_data)

    def _heuristic_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        dilemma = data.get("dilemma", "").lower()
        timeframe = data.get("timeframe", "6 months")
        hours = data.get("hours_per_week", 15)
        skills = data.get("current_skills", "Beginner student")
        goal = data.get("primary_goal", "Career advancement")

        # Heuristic determination of Path A & B from keywords
        if "web" in dilemma and ("ai" in dilemma or "python" in dilemma or "machine learning" in dilemma):
            path_a = "Python & AI/ML Specialist Path"
            path_b = "Full-Stack Web Development Path"
            conflict = "Theoretical depth and math-heavy modeling (AI) vs. rapid prototype building and immediate hiring volume (Web Dev)."
        elif "internship" in dilemma and ("study" in dilemma or "gpa" in dilemma or "course" in dilemma or "college" in dilemma):
            path_a = "Accept Internship (Hands-on Industry Experience)"
            path_b = "Focus on Academic Studies & GPA (Strong Foundation)"
            conflict = "Immediate real-world commercial experience vs. academic excellence and competitive GPA for higher studies."
        elif "job" in dilemma and ("masters" in dilemma or "higher" in dilemma or "gate" in dilemma):
            path_a = "Enter Job Market Immediately (Corporate Experience)"
            path_b = "Pursue Higher Studies / Master's Degree (Academic Specialization)"
            conflict = "Financial independence and industry seniority vs. advanced academic credentials and specialized research roles."
        else:
            path_a = "Path A: High-Specialization / Deep Tech Approach"
            path_b = "Path B: Applied Practical / Fast-To-Market Approach"
            conflict = "Long-term theoretical differentiation vs. short-term tangible deliverables and lower barrier to entry."

        return {
            "summary": f"The user is evaluating between two strategic trajectories over a {timeframe} horizon with {hours} hours/week available commitment.",
            "path_a_label": path_a,
            "path_b_label": path_b,
            "core_conflict": conflict,
            "timeline_months": int(str(timeframe).split()[0]) if str(timeframe).split() and str(timeframe).split()[0].isdigit() else 6,
            "hours_per_week": hours,
            "current_level": skills,
            "target_milestone": goal,
            "key_constraints": [
                f"Time allocation ceiling of {hours} hours/week",
                f"Evaluation horizon fixed at {timeframe}",
                f"Starting from baseline: {skills}"
            ],
            "key_success_factors": [
                "Consistent high-yield weekly execution without burnout",
                "Building 2-3 production-grade portfolio projects",
                "Aligning learning milestones directly with entry-level job descriptions"
            ]
        }

