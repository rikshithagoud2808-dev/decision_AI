import os
from pathlib import Path
from flask import Flask
from config import Config
from app.models import init_db
from app.routes import main_bp

# Set absolute paths for templates and static folders inside app/
BASE_DIR = Path(__file__).resolve().parent
template_dir = str(BASE_DIR / "app" / "templates")
static_dir = str(BASE_DIR / "app" / "static")

# Expose the Flask application
app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)
app.config.from_object(Config)

# Initialize SQLite database
init_db()

# Register existing routes blueprint
app.register_blueprint(main_bp)

if __name__ == "__main__":
    port = Config.PORT
    print(f"\n==================================================================")
    print(f"  DecisionAI: Personal Decision Simulation & Recommendation System")
    print(f"  Running on http://127.0.0.1:{port}")
    print(f"==================================================================\n")
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)

