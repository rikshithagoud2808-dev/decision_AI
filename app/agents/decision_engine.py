import json
import logging
from typing import Dict, Any, List
from app.agents.llm_client import LLMClient
from app.agents.analyzer import SituationAnalyzer
from app.agents.simulator import FutureSimulator
from app.agents.critic import DecisionCritic

logger = logging.getLogger("decision_ai.engine")

class DecisionEngine:
    """
    Decision Engine & Orchestrator
    1. Runs the multi-agent pipeline: SituationAnalyzer -> FutureSimulator -> DecisionCritic
    2. Computes multi-criteria decision scores (0-10 & 0-100 normalized)
    3. Resolves the trade-offs and generates a final synthesized recommendation,
       hybrid strategy, and execution roadmap.
    """
    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.analyzer = SituationAnalyzer(self.llm)
        self.simulator = FutureSimulator(self.llm)
        self.critic = DecisionCritic(self.llm)

    def run_full_simulation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the entire 4-stage pipeline and returns the complete decision report.
        """
        logger.info(f"Starting DecisionAI pipeline for dilemma: {user_data.get('dilemma')}")

        # Stage 1: Situation Analyzer
        analysis = self.analyzer.analyze(user_data)

        # Stage 2: Future Simulator
        simulation = self.simulator.simulate(analysis, user_data)

        # Stage 3: Decision Critic
        critique = self.critic.critique(analysis, simulation, user_data)

        # Stage 4: Scoring & Synthesis
        scores = self._calculate_decision_scores(user_data, analysis, simulation, critique)
        synthesis = self._synthesize_recommendation(user_data, analysis, simulation, critique, scores)
        roadmap = self._generate_roadmap(synthesis.get("recommended_path"), simulation, user_data)

        return {
            "dilemma": user_data.get("dilemma"),
            "user_profile": {
                "timeframe": user_data.get("timeframe", "6 months"),
                "hours_per_week": int(user_data.get("hours_per_week", 15)),
                "current_skills": user_data.get("current_skills", "Beginner"),
                "primary_goal": user_data.get("primary_goal", "Career advancement"),
                "risk_tolerance": user_data.get("risk_tolerance", "Moderate")
            },
            "situation_analysis": analysis,
            "future_simulation": simulation,
            "decision_critique": critique,
            "decision_scores": scores,
            "final_synthesis": synthesis,
            "action_roadmap": roadmap
        }

    def _calculate_decision_scores(self, user_data: Dict[str, Any], analysis: Dict[str, Any], 
                                  sim: Dict[str, Any], critique: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multi-criteria quantitative scoring algorithm.
        Outputs scores on 0-10 scale for Chart.js radar & bar comparisons, plus 0-100 overall fit.
        """
        hours = int(user_data.get("hours_per_week", 15))
        dilemma = user_data.get("dilemma", "").lower()

        path_a = sim.get("path_a", {})
        path_b = sim.get("path_b", {})
        crit_a = critique.get("path_a_critique", {})
        crit_b = critique.get("path_b_critique", {})

        # Default scoring baselines
        if "ai" in dilemma or "python" in dilemma or "web" in dilemma:
            diff_a = 8.2
            diff_b = 6.0
            time_a = 6.0  # months
            time_b = 4.0  # months
            growth_a = 9.2
            growth_b = 8.0
            opps_a = 8.0
            opps_b = 9.3
            market_demand_a = 8.5
            market_demand_b = 9.5
        else:
            diff_a = 7.8
            diff_b = 6.2
            time_a = 5.5
            time_b = 3.5
            growth_a = 8.8
            growth_b = 7.5
            opps_a = 8.0
            opps_b = 8.6
            market_demand_a = 8.0
            market_demand_b = 8.8

        burnout_a = crit_a.get("burnout_risk_score", 7)
        burnout_b = crit_b.get("burnout_risk_score", 5)

        # Feasibility score influenced by available weekly hours
        # If user has >= 20 hrs/week, deep/difficult paths become much more feasible
        feasibility_a = max(20, min(95, int(100 - (diff_a * 5) - (max(0, 20 - hours) * 2.5))))
        feasibility_b = max(40, min(98, int(100 - (diff_b * 4) - (max(0, 15 - hours) * 1.5))))

        # Weighted composite fit calculation
        # Weights: Feasibility 30%, Market Demand 25%, Skill Growth 25%, Burnout Risk 20% (inverted)
        fit_a = int((feasibility_a * 0.35) + (market_demand_a * 10 * 0.25) + (growth_a * 10 * 0.25) + ((10 - burnout_a) * 10 * 0.15))
        fit_b = int((feasibility_b * 0.35) + (market_demand_b * 10 * 0.25) + (growth_b * 10 * 0.25) + ((10 - burnout_b) * 10 * 0.15))

        return {
            "path_a": {
                "name": path_a.get("title", "Path A"),
                "difficulty": diff_a,
                "time_required_months": time_a,
                "skill_growth": growth_a,
                "project_opportunities": opps_a,
                "market_demand": market_demand_a,
                "burnout_risk": burnout_a,
                "feasibility_score": feasibility_a,
                "overall_fit_score": fit_a
            },
            "path_b": {
                "name": path_b.get("title", "Path B"),
                "difficulty": diff_b,
                "time_required_months": time_b,
                "skill_growth": growth_b,
                "project_opportunities": opps_b,
                "market_demand": market_demand_b,
                "burnout_risk": burnout_b,
                "feasibility_score": feasibility_b,
                "overall_fit_score": fit_b
            },
            "radar_dimensions": [
                "Feasibility with your Hours",
                "Market Demand & Job Openings",
                "Skill Growth Potential",
                "Portfolio Impact",
                "Speed to Market / Low Friction"
            ],
            "radar_series_a": [
                round(feasibility_a / 10, 1),
                market_demand_a,
                growth_a,
                opps_a,
                round(10 - diff_a, 1)
            ],
            "radar_series_b": [
                round(feasibility_b / 10, 1),
                market_demand_b,
                growth_b,
                opps_b,
                round(10 - diff_b, 1)
            ]
        }

    def _synthesize_recommendation(self, user_data: Dict[str, Any], analysis: Dict[str, Any],
                                  sim: Dict[str, Any], critique: Dict[str, Any],
                                  scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes the multi-agent findings into a final authoritative recommendation,
        calculating confidence, rationale, and a hybrid compromise strategy.
        """
        path_a_title = sim.get("path_a", {}).get("title", "Path A")
        path_b_title = sim.get("path_b", {}).get("title", "Path B")
        score_a = scores["path_a"]["overall_fit_score"]
        score_b = scores["path_b"]["overall_fit_score"]
        hours = int(user_data.get("hours_per_week", 15))
        timeframe = user_data.get("timeframe", "6 months")

        if score_b >= score_a:
            winner = "Path B"
            winner_title = path_b_title
            runner_up_title = path_a_title
            confidence = min(92, max(75, 70 + (score_b - score_a) * 2))
            reasoning = (
                f"Based on your constraint of {hours} hours/week over {timeframe}, {path_b_title} "
                f"is recommended. It offers a significantly faster time-to-market (4 months vs 6 months), "
                f"a higher volume of entry-level internship openings, and lower initial burnout risk. "
                f"You can achieve high portfolio credibility before encountering deep prerequisite hurdles."
            )
            why_not_other = (
                f"While {path_a_title} provides high theoretical growth, dedicating under 20 hrs/week "
                f"creates substantial risk of stalling in math/theory prerequisites before producing an "
                f"internship-ready portfolio project."
            )
            hybrid_strategy = (
                f"The 'Trojan Horse' Hybrid Strategy: Pursue {path_b_title} for the first 3-4 months "
                f"to master frontend, APIs, and database fundamentals. Then, in months 5-6, build an AI-powered "
                f"feature (integrating LLM APIs / LangChain into your web app). This makes you an 'AI-Enhanced Full Stack Developer', "
                f"giving you the high marketability of Web Dev with the prestige of modern AI!"
            )
        else:
            winner = "Path A"
            winner_title = path_a_title
            runner_up_title = path_b_title
            confidence = min(92, max(75, 70 + (score_a - score_b) * 2))
            reasoning = (
                f"With your dedicated time commitment, {path_a_title} is recommended. "
                f"The long-term technical moat, higher compensation trajectory, and intellectual upside "
                f"outweigh the steeper initial learning curve."
            )
            why_not_other = (
                f"While {path_b_title} is faster to enter, entry-level web development is heavily crowded. "
                f"Your profile allows you to break into higher-tier specialized opportunities."
            )
            hybrid_strategy = (
                f"Build practical full-stack demonstration interfaces for all your AI models so recruiters "
                f"can interactively test your systems directly in the browser."
            )

        return {
            "recommended_path": winner,
            "recommended_title": winner_title,
            "runner_up_title": runner_up_title,
            "confidence_score": f"{confidence}%",
            "executive_summary": reasoning,
            "counter_argument_defense": why_not_other,
            "hybrid_strategy": hybrid_strategy,
            "success_probability": f"{min(95, confidence + 3)}%"
        }

    def _generate_roadmap(self, recommended_path: str, sim: Dict[str, Any], user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates a 6-month actionable step-by-step roadmap for the user.
        """
        dilemma_lower = user_data.get("dilemma", "").lower()
        is_web = (recommended_path == "Path B" and ("ai" in dilemma_lower or "web" in dilemma_lower))

        if is_web:
            return [
                {
                    "phase": "Month 1",
                    "milestone": "Frontend Core & Responsive Systems",
                    "focus": "Modern JavaScript (ES6+), DOM, Tailwind CSS, Component Architecture",
                    "deliverable": "A responsive, accessible portfolio site and a dynamic interactive data dashboard."
                },
                {
                    "phase": "Month 2",
                    "milestone": "React.js & State Management",
                    "focus": "React hooks, component lifecycles, API consumption, routing, state libraries",
                    "deliverable": "Interactive CRUD Application with search, filtering, and local persistence."
                },
                {
                    "phase": "Month 3",
                    "milestone": "Backend APIs & Databases",
                    "focus": "Node.js/Express or Python FastAPI/Flask, PostgreSQL/SQLite, JWT Authentication",
                    "deliverable": "Production REST API with user auth, token refresh, and relational database schema."
                },
                {
                    "phase": "Month 4",
                    "milestone": "Full-Stack Integration & Capstone Alpha",
                    "focus": "Connecting frontend with custom backend, error handling, Docker basics, deployment",
                    "deliverable": "Live deployed SaaS Task / Collaboration Hub with real-time updates."
                },
                {
                    "phase": "Month 5",
                    "milestone": "AI Feature Integration (The Hybrid Edge)",
                    "focus": "LLM API integration (Gemini / OpenAI), prompt engineering, vector search, streaming UI",
                    "deliverable": "AI Copilot feature embedded inside your full-stack capstone project."
                },
                {
                    "phase": "Month 6",
                    "milestone": "Internship Outreach & Mock Interviews",
                    "focus": "Resume optimization, GitHub README polish, LeetCode Easy/Medium, cold reachouts",
                    "deliverable": "Active application pipeline: 15 targeted internship submissions per week."
                }
            ]
        else:
            return [
                {
                    "phase": "Month 1",
                    "milestone": "Foundational Mastery & Environment Setup",
                    "focus": "Core principles, algorithmic problem solving, toolchain configuration",
                    "deliverable": "Structured repository with foundational proof-of-concept scripts."
                },
                {
                    "phase": "Month 2",
                    "milestone": "Intermediate Techniques & Architecture",
                    "focus": "Data handling, library ecosystems, system modularity, design patterns",
                    "deliverable": "First standalone working prototype demonstrating technical execution."
                },
                {
                    "phase": "Month 3",
                    "milestone": "Advanced Specialization & Edge Cases",
                    "focus": "Optimization, advanced frameworks, debugging complex error states",
                    "deliverable": "End-to-end project addressing a non-trivial domain challenge."
                },
                {
                    "phase": "Month 4",
                    "milestone": "Production Packaging & Deployment",
                    "focus": "API wrapping, deployment pipelines, documentation, test coverage",
                    "deliverable": "Live hosted showcase accessible via public URL."
                },
                {
                    "phase": "Month 5",
                    "milestone": "Adversarial Stress Testing & Polish",
                    "focus": "Refining edge cases, optimizing latency/performance, README writeups",
                    "deliverable": "Comprehensive case study published on GitHub and LinkedIn."
                },
                {
                    "phase": "Month 6",
                    "milestone": "Industry Outreach & Review",
                    "focus": "Reaching out to engineering managers, portfolio reviews, viva preparation",
                    "deliverable": "Direct interview pipelines and viva-ready project demonstration."
                }
            ]

