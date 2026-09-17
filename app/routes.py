import logging
from flask import Blueprint, render_template, request, jsonify
from app.agents.decision_engine import DecisionEngine
from app.agents.llm_client import LLMClient
from app.models import save_simulation, get_all_simulations, get_simulation_by_id, delete_simulation
from config import Config

logger = logging.getLogger("decision_ai.routes")
main_bp = Blueprint("main", __name__)

# Active decision engine instance
engine = DecisionEngine()

@main_bp.route("/")
def index():
    """Renders the main decision dashboard."""
    return render_template("index.html")

@main_bp.route("/api/status", methods=["GET"])
def get_status():
    """Returns the current operational status of the AI engine."""
    provider = engine.llm.get_active_provider()
    has_key = engine.llm.has_valid_key()
    
    if provider == "openai":
        mode = "OpenAI Live API (GPT-4o-mini)"
        model = engine.llm.openai_model
    elif provider == "gemini":
        mode = "Gemini Live API (1.5 Flash)"
        model = engine.llm.gemini_model
    else:
        mode = "High-Fidelity Simulation Engine (Offline Ready)"
        model = "heuristic-multi-agent"

    return jsonify({
        "status": "online",
        "provider": provider,
        "mode": mode,
        "has_api_key": has_key,
        "model": model
    })

@main_bp.route("/api/simulate", methods=["POST"])
def simulate_decision():
    """
    Executes the multi-agent decision pipeline for the user's input.
    Saves the generated report into SQLite and returns the full structured response.
    """
    try:
        data = request.get_json() or {}
        dilemma = data.get("dilemma", "").strip()
        if not dilemma:
            return jsonify({"error": "Please enter a decision dilemma."}), 400

        user_data = {
            "dilemma": dilemma,
            "timeframe": data.get("timeframe", "6 months"),
            "hours_per_week": int(data.get("hours_per_week", 15)),
            "current_skills": data.get("current_skills", "Beginner / Some coding knowledge"),
            "primary_goal": data.get("primary_goal", "Internship / Job Readiness"),
            "risk_tolerance": data.get("risk_tolerance", "Moderate")
        }

        # Run multi-agent simulation
        report = engine.run_full_simulation(user_data)

        # Save to SQLite
        sim_id = save_simulation(report)
        report["id"] = sim_id

        return jsonify({"success": True, "report": report})

    except Exception as e:
        logger.error(f"Error in simulate_decision: {e}", exc_info=True)
        return jsonify({"error": f"Simulation failed: {str(e)}"}), 500

@main_bp.route("/api/history", methods=["GET"])
def get_history():
    """Returns past simulations from SQLite."""
    try:
        simulations = get_all_simulations()
        return jsonify({"success": True, "simulations": simulations})
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({"error": str(e)}), 500

@main_bp.route("/api/history/<int:sim_id>", methods=["GET"])
def get_history_item(sim_id: int):
    """Retrieves a specific simulation by ID."""
    try:
        sim = get_simulation_by_id(sim_id)
        if not sim:
            return jsonify({"error": "Simulation not found"}), 404
        return jsonify({"success": True, "simulation": sim})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route("/api/history/<int:sim_id>", methods=["DELETE"])
def delete_history_item(sim_id: int):
    """Deletes a simulation by ID."""
    try:
        success = delete_simulation(sim_id)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route("/api/configure_key", methods=["POST"])
def configure_key():
    """Updates the OpenAI or Gemini API key in runtime."""
    try:
        data = request.get_json() or {}
        openai_key = data.get("openai_key", "").strip()
        gemini_key = data.get("gemini_key", "").strip()
        new_key = data.get("api_key", "").strip()

        if openai_key:
            engine.llm.openai_key = openai_key
        elif new_key and new_key.startswith("sk-"):
            engine.llm.openai_key = new_key

        if gemini_key:
            engine.llm.gemini_key = gemini_key
        elif new_key and new_key.startswith("AIza"):
            engine.llm.gemini_key = new_key

        provider = engine.llm.get_active_provider()
        has_key = engine.llm.has_valid_key()

        return jsonify({
            "success": True,
            "has_api_key": has_key,
            "provider": provider,
            "mode": f"{provider.upper()} Live API" if has_key else "Simulation Engine (Offline Ready)"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

