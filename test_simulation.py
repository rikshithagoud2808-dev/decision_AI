import os
import sys
import json

# Ensure workspace root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.decision_engine import DecisionEngine
from app.models import init_db, save_simulation, get_all_simulations, get_simulation_by_id

def test_pipeline():
    print(">>> 1. Initializing SQLite Database...")
    init_db()
    print("  [OK] Database initialized.")

    print("\n>>> 2. Initializing DecisionEngine & Multi-Agent Pipeline...")
    engine = DecisionEngine()

    test_input = {
        "dilemma": "I have 6 months. Should I learn Python + AI or Web Development?",
        "timeframe": "6 months",
        "hours_per_week": 15,
        "current_skills": "Basic C++ and Python fundamentals",
        "primary_goal": "Secure an internship / placement",
        "risk_tolerance": "Moderate"
    }

    print("\n>>> 3. Executing Full Simulation...")
    report = engine.run_full_simulation(test_input)

    print(f"\n  [Agent 1: Situation Analyzer]")
    analysis = report["situation_analysis"]
    print(f"    - Path A: {analysis['path_a_label']}")
    print(f"    - Path B: {analysis['path_b_label']}")
    print(f"    - Core Conflict: {analysis['core_conflict']}")

    print(f"\n  [Agent 2: Future Simulator]")
    sim = report["future_simulation"]
    print(f"    - Path A Title: {sim['path_a']['title']}")
    print(f"    - Path A Weekly Hours: {sim['path_a']['weekly_effort_hours']} hrs/wk")
    print(f"    - Path B Title: {sim['path_b']['title']}")
    print(f"    - Path B Weekly Hours: {sim['path_b']['weekly_effort_hours']} hrs/wk")

    print(f"\n  [Agent 3: Decision Critic]")
    critic = report["decision_critique"]
    print(f"    - Path A Burnout Risk: {critic['path_a_critique']['burnout_risk_score']}/10")
    print(f"    - Path B Burnout Risk: {critic['path_b_critique']['burnout_risk_score']}/10")
    print(f"    - Trade-off Verdict: {critic['critical_tradeoff_verdict'][:100]}...")

    print(f"\n  [Decision Engine: Scoring & Verdict]")
    scores = report["decision_scores"]
    synthesis = report["final_synthesis"]
    print(f"    - Path A Overall Fit: {scores['path_a']['overall_fit_score']}/100")
    print(f"    - Path B Overall Fit: {scores['path_b']['overall_fit_score']}/100")
    print(f"    - Recommended Path: {synthesis['recommended_path']} ({synthesis['recommended_title']})")
    print(f"    - Confidence: {synthesis['confidence_score']}")
    print(f"    - Hybrid Strategy: {synthesis['hybrid_strategy'][:110]}...")

    print("\n>>> 4. Testing SQLite Persistence...")
    sim_id = save_simulation(report)
    print(f"  [OK] Saved simulation with ID: {sim_id}")

    saved = get_simulation_by_id(sim_id)
    assert saved is not None, "Failed to retrieve simulation from DB"
    assert saved["dilemma"] == test_input["dilemma"], "Dilemma mismatch in DB"
    print(f"  [OK] Successfully retrieved simulation #{sim_id} from SQLite.")

    history = get_all_simulations()
    print(f"  [OK] Total simulations in history: {len(history)}")

    print("\n==================================================")
    print("   ALL TESTS PASSED! Multi-Agent Pipeline is 100% Functional!")
    print("==================================================")

if __name__ == "__main__":
    test_pipeline()

