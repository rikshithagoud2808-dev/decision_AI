import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP NOT NULL,
            dilemma TEXT NOT NULL,
            timeframe TEXT,
            hours_per_week INTEGER,
            recommended_path TEXT,
            recommended_title TEXT,
            confidence_score TEXT,
            report_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_simulation(report: Dict[str, Any]) -> int:
    """Saves a simulation report to SQLite and returns the inserted ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    dilemma = report.get("dilemma", "Untitled Decision")
    user_prof = report.get("user_profile", {})
    timeframe = user_prof.get("timeframe", "6 months")
    hours = user_prof.get("hours_per_week", 15)
    synthesis = report.get("final_synthesis", {})
    rec_path = synthesis.get("recommended_path", "Path B")
    rec_title = synthesis.get("recommended_title", "Recommended Path")
    conf = synthesis.get("confidence_score", "85%")
    report_json_str = json.dumps(report)

    cursor.execute("""
        INSERT INTO simulations (
            created_at, dilemma, timeframe, hours_per_week,
            recommended_path, recommended_title, confidence_score, report_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        dilemma,
        timeframe,
        hours,
        rec_path,
        rec_title,
        conf,
        report_json_str
    ))
    
    sim_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return sim_id

def get_all_simulations(limit: int = 50) -> List[Dict[str, Any]]:
    """Returns past simulations sorted by newest first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, created_at, dilemma, timeframe, hours_per_week,
               recommended_path, recommended_title, confidence_score
        FROM simulations
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_simulation_by_id(sim_id: int) -> Optional[Dict[str, Any]]:
    """Fetches a complete simulation report by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM simulations WHERE id = ?", (sim_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data["report"] = json.loads(data["report_json"])
    return data

def delete_simulation(sim_id: int) -> bool:
    """Deletes a simulation by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM simulations WHERE id = ?", (sim_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

