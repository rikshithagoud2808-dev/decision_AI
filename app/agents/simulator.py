import json
import logging
from typing import Dict, Any
from app.agents.llm_client import LLMClient

logger = logging.getLogger("decision_ai.simulator")

class FutureSimulator:
    """
    Agent 2: Future Simulator
    Projects and models the parallel future scenarios (Path A vs Path B).
    For each path, creates realistic milestones, skill curricula, project requirements,
    difficulty estimates, and readiness timelines.
    """
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def simulate(self, analysis: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        path_a_name = analysis.get("path_a_label", "Path A")
        path_b_name = analysis.get("path_b_label", "Path B")
        dilemma = user_data.get("dilemma", "")
        timeframe = user_data.get("timeframe", "6 months")
        hours_per_week = user_data.get("hours_per_week", 15)

        system_instruction = """
You are the "Future Simulator" Agent in a Multi-Agent Life Decision Simulation System.
Given the situation analysis and the two competing paths, simulate both futures realistically over the designated timeframe.

Be concrete and tailored to students/early-career builders. Do not give generic advice. Give specific technologies, realistic portfolio project titles, concrete weekly hour commitments, and real bottlenecks.

Return JSON in this exact structure:
{
  "path_a": {
    "title": "Title for Path A",
    "tagline": "Punchy 1-line summary of this trajectory",
    "narrative": "Paragraph describing what months 1 through 6 look like in this path",
    "skills_to_learn": ["Skill 1", "Skill 2", "Skill 3", "Skill 4"],
    "weekly_effort_hours": 18,
    "timeline_to_readiness_months": 5,
    "milestone_projects": [
      {"name": "Project 1 Title", "description": "What it does & tech used"},
      {"name": "Project 2 Title", "description": "What it does & tech used"}
    ],
    "expected_difficulties": ["Difficulty 1", "Difficulty 2"],
    "internship_readiness": "Assessment of job readiness (e.g., High / Moderate / Requires portfolio)",
    "future_opportunities": ["Opportunity 1", "Opportunity 2"],
    "daily_life_preview": "A glimpse into a typical day or study session"
  },
  "path_b": {
    "title": "Title for Path B",
    "tagline": "Punchy 1-line summary of this trajectory",
    "narrative": "Paragraph describing what months 1 through 6 look like in this path",
    "skills_to_learn": ["Skill 1", "Skill 2", "Skill 3", "Skill 4"],
    "weekly_effort_hours": 14,
    "timeline_to_readiness_months": 4,
    "milestone_projects": [
      {"name": "Project 1 Title", "description": "What it does & tech used"},
      {"name": "Project 2 Title", "description": "What it does & tech used"}
    ],
    "expected_difficulties": ["Difficulty 1", "Difficulty 2"],
    "internship_readiness": "Assessment of job readiness",
    "future_opportunities": ["Opportunity 1", "Opportunity 2"],
    "daily_life_preview": "A glimpse into a typical day or study session"
  }
}
"""

        user_input_prompt = f"""
Decision: {dilemma}
Path A: {path_a_name}
Path B: {path_b_name}
Available Time: {timeframe} ({hours_per_week} hours/week)
Current Baseline: {analysis.get('current_level')}
Goal: {analysis.get('target_milestone')}
Constraints: {analysis.get('key_constraints')}
"""

        result = self.llm.generate_json(system_instruction, user_input_prompt)
        if result and "path_a" in result and "path_b" in result:
            logger.info("Future Simulator completed using LLM.")
            return result

        logger.info("Using heuristic simulation engine for Future Simulator.")
        return self._heuristic_simulation(analysis, user_data)

    def _heuristic_simulation(self, analysis: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        path_a_label = analysis.get("path_a_label", "Path A: Advanced AI/ML Specialist")
        path_b_label = analysis.get("path_b_label", "Path B: Full-Stack Web Developer")
        dilemma_lower = data.get("dilemma", "").lower()
        hours = int(data.get("hours_per_week", 15))

        if "ai" in dilemma_lower or "python" in dilemma_lower or "web" in dilemma_lower:
            return {
                "path_a": {
                    "title": "Python & AI / Machine Learning Specialist",
                    "tagline": "High-ceiling, math-rigorous track creating intelligent algorithms & LLM applications",
                    "narrative": "Months 1-2 focus on advanced Python, NumPy, Pandas, and statistics foundations. Months 3-4 dive into Scikit-learn, PyTorch, and fine-tuning HuggingFace models. Months 5-6 culminate in building deployed RAG (Retrieval-Augmented Generation) agents.",
                    "skills_to_learn": [
                        "Python OOP & Data Structures",
                        "NumPy, Pandas, Data Preprocessing",
                        "PyTorch & Deep Learning Fundamentals",
                        "LangChain, Vector DBs (Chroma/FAISS) & RAG Systems",
                        "FastAPI & Model Deployment (Hugging Face / Docker)"
                    ],
                    "weekly_effort_hours": max(hours, 18),
                    "timeline_to_readiness_months": 6,
                    "milestone_projects": [
                        {"name": "Multi-Modal Document Querying Agent", "description": "RAG pipeline that extracts tabular data from PDFs using LangChain and Gemini/Llama"},
                        {"name": "Real-Time Predictive Analytics Dashboard", "description": "End-to-end ML model deployed with FastAPI predicting student performance trends"}
                    ],
                    "expected_difficulties": [
                        "Steep learning curve in Linear Algebra, Calculus, and model evaluation metrics",
                        "High compute requirements (GPU access, CUDA setup bottlenecks)",
                        "Junior AI positions often favor candidates with Master's or research publications"
                    ],
                    "internship_readiness": "Moderate (Requires outstanding niche projects to beat Master's grads)",
                    "future_opportunities": [
                        "AI Engineer / GenAI Developer",
                        "Machine Learning Ops (MLOps) Specialist",
                        "Data Scientist in FinTech & HealthTech"
                    ],
                    "daily_life_preview": "Reading research papers, debugging tensor dimension mismatches, tuning prompt temperatures, and monitoring vector retrieval latencies."
                },
                "path_b": {
                    "title": "Full-Stack Web Developer",
                    "tagline": "Immediate marketability, tangible product builds, and massive junior hiring pipeline",
                    "narrative": "Months 1-2 master modern JavaScript/TypeScript, React/Next.js, and CSS frameworks. Months 3-4 build REST APIs, authentication, and database schemas with Node.js/Python and PostgreSQL. Months 5-6 focus on testing, CI/CD, and portfolio deployment.",
                    "skills_to_learn": [
                        "Modern JavaScript (ES6+), React.js, Tailwind CSS",
                        "Backend APIs with Node.js (Express) or Python (Flask/FastAPI)",
                        "Database Management (PostgreSQL, SQLite, Prisma ORM)",
                        "Authentication (JWT/OAuth), Git Workflows & Vercel/Render Deployments"
                    ],
                    "weekly_effort_hours": hours,
                    "timeline_to_readiness_months": 4,
                    "milestone_projects": [
                        {"name": "Collaborative SaaS Task & Workspace Manager", "description": "Full-stack web app with real-time WebSockets, drag-and-drop boards, and team permissions"},
                        {"name": "E-Commerce Micro-Storefront with Stripe", "description": "Production-grade online catalog with secure payment checkout, cart state, and order tracking"}
                    ],
                    "expected_difficulties": [
                        "Frontend framework fatigue (fast-moving ecosystem and configuration boilerplate)",
                        "High competition at the entry level requires visually polished UI/UX",
                        "Balancing frontend state management with robust database error handling"
                    ],
                    "internship_readiness": "Very High (Highest volume of junior developer openings & startup internships)",
                    "future_opportunities": [
                        "Frontend / Full-Stack Software Engineer",
                        "SaaS Product Engineer",
                        "Freelance Web App Consultant / Startup Tech Lead"
                    ],
                    "daily_life_preview": "Building responsive UI components, wiring up REST endpoints, inspecting browser network tabs, and polishing user interactions."
                }
            }

        # General scenario fallback
        return {
            "path_a": {
                "title": path_a_label,
                "tagline": "Specialized deep-focus approach with high prestige and long-term leverage",
                "narrative": f"Over the next {timeframe}, you dedicate deliberate practice to build specialized competence. Early months encounter steep learning barriers, but yields significant differentiation.",
                "skills_to_learn": ["Core Conceptual Mastery", "Advanced Tooling", "Analytical Problem Solving", "Production Portfolio"],
                "weekly_effort_hours": max(hours, 16),
                "timeline_to_readiness_months": 5,
                "milestone_projects": [
                    {"name": "Capstone Project Alpha", "description": "End-to-end technical demonstration highlighting advanced domain expertise"},
                    {"name": "Industry Case Study", "description": "Structured real-world problem solution published on GitHub / Medium"}
                ],
                "expected_difficulties": ["Steep initial theoretical slope", "Slower immediate gratification in the first 60 days"],
                "internship_readiness": "High with rigorous portfolio proof",
                "future_opportunities": ["Specialist Consultant", "Domain Technical Lead", "High-growth niche engineering roles"],
                "daily_life_preview": "Deep work sessions, rigorous problem dissection, and continuous iterative testing."
            },
            "path_b": {
                "title": path_b_label,
                "tagline": "High-velocity, pragmatic approach emphasizing rapid outcomes and broad demand",
                "narrative": f"Within {timeframe}, you prioritize immediately marketable output. You build working prototypes quickly and validate them against real market demands.",
                "skills_to_learn": ["Agile Prototyping", "Widely Adopted Frameworks", "Client Communication", "Deployment & Delivery"],
                "weekly_effort_hours": hours,
                "timeline_to_readiness_months": 3,
                "milestone_projects": [
                    {"name": "MVP Launch Prototype", "description": "Functional solution addressing an active industry friction point"},
                    {"name": "Integration Service", "description": "API-driven service delivering immediate customer utility"}
                ],
                "expected_difficulties": ["Broad surface area of tools to learn", "Differentiation in crowded entry markets"],
                "internship_readiness": "Very High (Immediate applicability to existing team workflows)",
                "future_opportunities": ["Generalist Software Engineer", "Product Solutions Architect", "Startup Operator"],
                "daily_life_preview": "Rapid building sprints, connecting APIs, deploying updates, and demoing features."
            }
        }

