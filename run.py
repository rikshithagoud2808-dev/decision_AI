import sys
from app import create_app
from config import Config

app = create_app()

if __name__ == "__main__":
    port = Config.PORT
    print(f"\n==================================================================")
    print(f"  DecisionAI: Personal Decision Simulation & Recommendation System")
    print(f"  Running on http://127.0.0.1:{port}")
    print(f"==================================================================\n")
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)

