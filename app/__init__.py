import logging
from flask import Flask
from config import Config
from app.models import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)

    # Initialize SQLite database
    init_db()

    # Register routes blueprint
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app

# Expose default application instance
app = create_app()


