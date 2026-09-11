# 🧭 DecisionAI: A Generative AI-Based Personal Decision Simulation and Recommendation System

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-000000?style=flat&logo=flask&logoColor=white)](https://palletsprojects.com/p/flask/)
[![Gemini](https://img.shields.io/badge/Google-Gemini_AI-4285F4?style=flat&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.0+-FF6384?style=flat&logo=chartdotjs&logoColor=white)](https://chartjs.org)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org)

> **"Don't just ask AI for an answer. Simulate your futures before you decide."**

DecisionAI is an agentic AI web application engineered for students and early-career engineers. When facing crucial career forks in the road (e.g., *“Should I learn Python + AI or Web Development in 6 months?”* or *“Startup internship vs Placements?”*), DecisionAI does not simply produce a one-size-fits-all chatbot answer.

Instead, it orchestrates **3 specialized AI agents** and a **Decision Engine** to branch out parallel future scenarios, stress-test them through adversarial criticism, and calculate multi-criteria decision scores with interactive visual analytics.

---

## 🏗️ Multi-Agent Architecture

```
                       +-----------------------+
                       | User Dilemma & Context|
                       | (Hours, Goal, Baseline|
                       +-----------+-----------+
                                   |
                                   v
                       [ Agent 1: Situation Analyzer ]
                       * Deconstructs core conflict
                       * Maps constraints & milestones
                                   |
                                   v
                       [ Agent 2: Future Simulator ]
                       * Simulates Path A (AI/ML)
                       * Simulates Path B (Web Dev)
                       * Projects milestones, effort & projects
                                   |
                                   v
                       [ Agent 3: Decision Critic ]
                       * Adversarial devil's advocate
                       * Audits burnout, hiring barriers & blind spots
                                   |
                                   v
                       [ Decision Engine & Scorer ]
                       * Multi-criteria quantitative scoring
                       * Synthesizes verdict & "Trojan Horse" hybrid strategy
                       * Generates 6-month actionable roadmap
                                   |
                     +-------------+-------------+
                     |                           |
                     v                           v
      [ Modern Interactive Dashboard ]    [ SQLite Persistence ]
      - Side-by-Side Path Cards           - Full Decision History
      - Radar & Metrics Comparison        - Instant Re-loading
      - Print / PDF Export for Viva
```

### The 3 Autonomous Agents:
1. **Agent 1: Situation Analyzer**
   - Dissects unstructured user dilemmas.
   - Extracts constraints: weekly hours available, baseline skill level, target timeline, risk tolerance.
   - Identifies the fundamental tension between the competing trajectories.
2. **Agent 2: Future Simulator**
   - Concurrently projects both futures (Path A vs Path B).
   - Generates realistic 6-month narratives, concrete milestone projects with tech stacks, weekly effort commitments, and time-to-readiness estimates.
3. **Agent 3: Decision Critic (Adversarial Stress Test)**
   - Serves as the skeptic / devil's advocate.
   - Flags tutorial-hell traps, hiring saturation, prerequisite gaps (e.g., advanced mathematics), and scores burnout probability.
   - Formulates concrete mitigation techniques to de-risk either path.
4. **Decision Engine (Synthesizer & Scorer)**
   - Computes weighted decision scores: *Feasibility*, *Market Demand*, *Skill Growth*, *Portfolio Impact*, and *Speed to Market*.
   - Renders radar comparisons and provides a definitive recommendation with confidence rating.
   - Produces the **"Trojan Horse" Hybrid Strategy** (e.g. mastering Web Dev first, then embedding AI capabilities to get the best of both worlds).
   - Maps out a month-by-month execution roadmap.

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.9 or higher
- Git & modern web browser

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your **Google Gemini API Key** if you have one:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=5000
```
> **Offline / Viva Ready**: If no API key is provided, DecisionAI automatically switches to its high-fidelity built-in simulation engine. You can demonstrate the full application even with zero internet or API quota!

### 3. Run the Automated Verification Test
```bash
python test_simulation.py
```

### 4. Launch the Web Application
```bash
python run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📊 Features & UI Highlights

- **Dynamic Quick Presets**: Instant one-click testing with realistic student dilemmas:
  - *AI vs Full-Stack Web Dev (6-month horizon)*
  - *Fast-paced Startup Internship vs Campus DSA Placements*
  - *Freelancing vs 9.0+ GPA for Master's Abroad*
- **Live Pipeline Visualizer**: Animated status cards showing all 3 agents and engine executing in sequence.
- **Chart.js Radar Visualizer**: Multi-axial radar chart comparing both options on Feasibility, Demand, Growth, Impact, and Speed.
- **Side-by-Side Path Matrices**: Parallel comparison of weekly commitments, milestone projects, and readiness timelines.
- **Adversarial Risk Audit**: Devil's advocate critique showing burnout meters and failure modes.
- **SQLite History Storage**: Automatically preserves all simulations; re-open any past simulation instantly.
- **Print / PDF Export**: Optimized print CSS ready to generate clean PDF documentation for college reports.

---

## 🎓 Viva & Project Interview Talking Points

| Viva Question | Best Answer |
|---|---|
| **Why not just use a single ChatGPT prompt?** | A single LLM prompt suffers from optimism bias, hallucinated timelines, and lacks structured adversarial checks. By separating the task into 3 specialized agents, the **Simulator** is free to explore potentials while the **Critic** is explicitly incentivized to find flaws and market saturation. The **Engine** then acts as an unbiased judge. |
| **How does the multi-criteria scoring work?** | The Decision Engine scores options across 5 dimensions: Feasibility (penalized if weekly hours < required effort), Market Demand, Skill Growth, Portfolio Impact, and Speed. It calculates a weighted composite fit score (0-100) taking user constraints into account. |
| **What if the student has very few hours per week?** | The engine dynamically detects time scarcity: high-difficulty paths (like AI requiring 18h/week) receive heavy feasibility penalties, shifting the recommendation toward high-leverage, fast-to-market paths like Web Dev or a hybrid compromise. |
| **Is the database scalable?** | The application uses SQLite with structured relational schema and JSON serialization, allowing zero-configuration local execution and effortless migration to PostgreSQL or MySQL for production. |

---

## 🛠️ Project Structure

```
decision/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── analyzer.py          # Agent 1: Situation Analyzer
│   │   ├── simulator.py         # Agent 2: Future Simulator
│   │   ├── critic.py            # Agent 3: Decision Critic
│   │   ├── decision_engine.py   # Decision Engine & Scorer
│   │   └── llm_client.py        # Gemini API client & fallback handler
│   ├── static/
│   │   ├── css/style.css        # Custom styling, animations & print CSS
│   │   └── js/main.js           # Chart.js radar charts & agent animations
│   ├── templates/
│   │   └── index.html           # Modern responsive dashboard
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # SQLite database schema & operations
│   └── routes.py                # REST API endpoints
├── .env.example
├── config.py
├── requirements.txt
├── run.py                       # Main server entrypoint
├── test_simulation.py           # End-to-end verification script
└── README.md
```

---

## 📄 License
MIT License. Built for student decision intelligence and agentic AI education.

